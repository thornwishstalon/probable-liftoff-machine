from umqtt.simple import MQTTClient


class MQTTWrapper:
    def __init__(self, id, broker_address, callback):
        self.id = id
        self.broker_address = broker_address
        self.callback = callback
        self.counter = 0
        self.client = None

    def initialize(self):
        port = 1883
        print("mqtt id: {}".format(self.id))
        print("broker: {}:{}".format(self.broker_address, port))
        self.client = MQTTClient(
            client_id=self.id, server=self.broker_address, port=port, keepalive=60
        )
        self.client.set_callback(self.callback)

    def disconnect(self):
        self.client.disconnect()

    def connect(self):
        self.client.connect()

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def run(self):
        self.counter += 1
        if self.counter % 10:
            self.client.ping()
            self.counter = 0
        self.client.check_msg()
