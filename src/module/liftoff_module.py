import gc
import network
import ubinascii as binascii
import utime as time
import ujson
from abc import abstractmethod

from common.credentials import Config
from common.mqtt_client import MQTTWrapper
from umqtt.simple import MQTTException


class LiftoffModule():
    AP_IP = "192.168.4.1"
    AP_OFF_DELAY = const(10 * 1000)
    MAX_CONN_ATTEMPTS = 10
    DEFAULT_SSID = b"liftoff"

    def __init__(self, config, lcd=None):
        self.local_ip = self.AP_IP
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.lcd = lcd
        self.config = config

        self.conn_time_start = None
        #
        self.host = None
        self.mqtt = None

    @abstractmethod
    @property
    def subscriber(self):
        raise NotImplemented()

    def callback(self, topic, message):
        self.subscriber.notify(topic, ujson.loads(message))

    def connect_to_broker(self):
        """ connects to broker and register to topic
        """
        print('connect to MQTT broker...')

        self.mqtt = MQTTWrapper(self.config.mqtt_id, self.config.mqtt_broker, self.callback)
        self.mqtt.initialize()
        self.mqtt.connect()
        print('subscribing to  MQTT topics ...')
        for topic in self.subscriber.subscriber_list.keys():
            print(topic)
            self.mqtt.subscribe(topic)

        if self.lcd:
            self.lcd.text("mqtt: ready", 0, 40)
            self.lcd.show()

    def start_access_point(self):
        # sometimes need to turn off AP before it will come up properly
        self.ap_if.active(False)
        while not self.ap_if.active():
            print("Waiting for access point to turn on")
            self.ap_if.active(True)
            time.sleep(1)
        # IP address, netmask, gateway, DNS
        self.ap_if.ifconfig(
            (self.local_ip, "255.255.255.0", self.local_ip, self.local_ip)
        )
        self.host = self.ap_if.ifconfig()[0]

        if self.config.ssid is None:
            # essid = b"ESP8266-%s" % binascii.hexlify(self.ap_if.config("mac")[-3:])
            self.config.ssid = self.DEFAULT_SSID

        if self.lcd:
            self.lcd.fill(0)
            self.lcd.text("{:s}".format(self.config.ssid), 0, 0)
            self.lcd.text("{}:{}".format(self.host, 80), 0, 20)
            self.lcd.show()

        self.ap_if.config(essid=self.config.ssid, authmode=network.AUTH_OPEN)
        print("AP mode configured:", self.ap_if.ifconfig())

    def connect_to_wifi(self):
        print(
            "Trying to connect to SSID '{:s}' with password {:s}".format(
                self.config.ssid, self.config.password
            )
        )

        # initiate the connection
        self.sta_if.active(True)
        self.sta_if.connect(self.config.ssid, self.config.password)

        attempts = 1
        while attempts <= self.MAX_CONN_ATTEMPTS:
            if not self.sta_if.isconnected():
                print("Connection attempt {:d}/{:d} ...".format(attempts, self.MAX_CONN_ATTEMPTS))
                time.sleep(2)
                attempts += 1
            else:
                print("Connected to {:s}".format(self.config.ssid))
                self.local_ip = self.sta_if.ifconfig()[0]
                return True

        print(
            "Failed to connect to {:s} with {:s}. WLAN status={:d}".format(
                self.config.ssid, self.config.password, self.sta_if.status()
            )
        )
        # forget the credentials since they didn't work, and turn off station mode
        self.config.remove()
        self.sta_if.active(False)
        return False

    def check_valid_wifi(self):
        if not self.sta_if.isconnected():
            if self.config.has_wifi():
                # have credentials to connect, but not yet connected
                # return value based on whether the connection was successful
                return self.connect_to_wifi()
            # not connected, and no credentials to connect yet
            return False

        if not self.ap_if.active():
            # access point is already off; do nothing
            return False

        # already connected to WiFi, so turn off Access Point after a delay
        if self.conn_time_start is None:
            self.conn_time_start = time.ticks_ms()
            remaining = self.AP_OFF_DELAY
        else:
            remaining = self.AP_OFF_DELAY - time.ticks_diff(
                time.ticks_ms(), self.conn_time_start
            )
            if remaining <= 0:
                self.ap_if.active(False)
                print("Turned off access point")
        return False

    def try_connect_from_file(self):
        print(self.config)
        if self.config.has_wifi():
            if self.connect_to_wifi():
                return True

        # WiFi Connection failed - remove credentials from disk
        self.config.remove()
        return False

    def liftoff(self):
        print("Starting Server")
        self.start_access_point()

        try:
            while True:
                if self.check_valid_wifi():
                    print("Connected to WiFi!")
                    break
                if self.ap_if.active() == True:
                    print("Access Point running!")
                    break


        except KeyboardInterrupt:
            print("Module stopped")
        self.cleanup()

    def start(self):
        # turn off station interface to force a reconnect
        self.sta_if.active(False)
        if not self.try_connect_from_file():
            self.liftoff()

        print("try connect to broker!")
        while True:
            try:
                self.connect_to_broker()
                break
            except (MQTTException, OSError) as e:
                print(str(e))
                print('Failed to connect to MQTT broker. Reconnecting...')
                time.sleep(5)

    def run(self, timer):
        try:
            if self.mqtt:
                self.mqtt.run()
        except OSError:
            self.connect_to_broker()

    def cleanup(self):
        gc.collect()

    def stop(self):
        if self.mqtt:
            self.mqtt.disconnect()
