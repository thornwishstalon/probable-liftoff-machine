import gc
import network
import ubinascii as binascii
import urequests as urequests
import uselect as select
import utime as time
from abc import abstractmethod

from module.http_server import HTTPServer
from common.credentials import Creds
from module.subscriber import SubscriberList


class LiftoffModule():
    AP_IP = "192.168.4.1"
    AP_OFF_DELAY = const(10 * 1000)
    MAX_CONN_ATTEMPTS = 10

    def __init__(self, essid=None):
        self.local_ip = self.AP_IP
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)

        if essid is None:
            essid = b"ESP8266-%s" % binascii.hexlify(self.ap_if.config("mac")[-3:])
        self.essid = essid

        self.creds = Creds()

        self.http_server = None
        self.poller = select.poll()

        self.conn_time_start = None

    @abstractmethod
    @property
    def routes(self):
        raise NotImplemented()

    @abstractmethod
    @property
    def subscriber(self):
        raise NotImplemented()

    @abstractmethod
    @property
    def part_of(self):
        """
        other modules might be waiting for this module to be ready
        """
        raise NotImplemented()

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
        self.ap_if.config(essid=self.essid, authmode=network.AUTH_OPEN)
        print("AP mode configured:", self.ap_if.ifconfig())

    def connect_to_wifi(self):
        print(
            "Trying to connect to SSID '{:s}' with password {:s}".format(
                self.creds.ssid, self.creds.password
            )
        )

        # initiate the connection
        self.sta_if.active(True)
        self.sta_if.connect(self.creds.ssid, self.creds.password)

        attempts = 1
        while attempts <= self.MAX_CONN_ATTEMPTS:
            if not self.sta_if.isconnected():
                print("Connection attempt {:d}/{:d} ...".format(attempts, self.MAX_CONN_ATTEMPTS))
                time.sleep(2)
                attempts += 1
            else:
                print("Connected to {:s}".format(self.creds.ssid))
                self.local_ip = self.sta_if.ifconfig()[0]
                return True

        print(
            "Failed to connect to {:s} with {:s}. WLAN status={:d}".format(
                self.creds.ssid, self.creds.password, self.sta_if.status()
            )
        )
        # forget the credentials since they didn't work, and turn off station mode
        self.creds.remove()
        self.sta_if.active(False)
        return False

    def check_valid_wifi(self):
        if not self.sta_if.isconnected():
            if self.creds.load().is_valid():
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

    def liftoff(self):
        print("Starting Server")
        self.start_access_point()
        if self.http_server is None:
            self.http_server = HTTPServer(self.poller, self.local_ip)
            print("Configured HTTP server")
            for key, value in self.routes.items():
                print('add module routes')
                self.http_server.add_route(key, value)
            print('add module subscriptions')
            self.http_server.set_subscriber(self.subscriber)
            print('register module subscriptions')
            self.register_subscriber_at_bus(self.subscriber, self.part_of)

        try:
            while True:
                gc.collect()
                # check for socket events and handle them
                for response in self.poller.ipoll(1000):
                    sock, event, *others = response
                    self.handle_http(sock, event, others)

                if self.check_valid_wifi():
                    print("Connected to WiFi!")
                    self.http_server.set_ip(self.local_ip, self.creds.ssid)
                    break

        except KeyboardInterrupt:
            print("Module stopped")
        self.cleanup()

    def handle_http(self, sock, event, others):
        self.http_server.handle(sock, event, others)

    def cleanup(self):
        gc.collect()

    def try_connect_from_file(self):
        if self.creds.load().is_valid():
            if self.connect_to_wifi():
                return True

        # WiFi Connection failed - remove credentials from disk
        self.creds.remove()
        return False

    def trigger_event(self, event_tag, event):
        response_ref = None
        try:
            url = 'http://192.168.4.1/event'
            headers = {'Connection': 'Close'}
            response_ref = urequests.post(url=url, headers=headers, data={'tag': event_tag, 'event': event})
            if response_ref.status_code == 200:
                # nothing to do here
                pass
            else:
                # oh boy!
                pass
        except Exception as e:
            print('exception occured: "%s"' % e)
        finally:
            # socket clean up
            if response_ref:
                response_ref.close()

    def _register_for_event(self, event_tag, priority):
        response_ref = None
        try:
            url = 'http://192.168.4.1/register'
            headers = {'Connection': 'Close'}
            response_ref = urequests.post(url=url, headers=headers, data={'tag': event_tag, 'priority': priority})
            if response_ref.status_code == 200:
                # nothing to do here
                pass
            else:
                # oh boy!
                pass
        except Exception as e:
            print('exception occured: "%s"' % e)
        finally:
            # socket clean up
            if response_ref:
                response_ref.close()

    def _contributes_for_event(self, event_tag):
        response_ref = None
        try:
            url = 'http://192.168.4.1/contribute'
            headers = {'Connection': 'Close'}
            response_ref = urequests.post(url=url, headers=headers, data={'tag': event_tag})
            if response_ref.status_code == 200:
                # nothing to do here
                pass
            else:
                # oh boy!
                pass
        except Exception as e:
            print('exception occured: "%s"' % e)
        finally:
            # socket clean up
            if response_ref:
                response_ref.close()

    def start(self):
        # turn off station interface to force a reconnect
        self.sta_if.active(False)
        if not self.try_connect_from_file():
            self.liftoff()

    def register_subscriber_at_bus(self, subscriber: SubscriberList, part_of):
        for tag in subscriber.subscriber_list.keys():
            self._register_for_event(tag, subscriber.priority)

        for tag in part_of:
            self._contributes_for_event(tag)
