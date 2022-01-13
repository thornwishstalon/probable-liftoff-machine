from umqttsimple import MQTTClient


class MQTTWrapper:
    def __init__(self, id, broker_address, callback):
        self.id = id
        self.broker_address = broker_address
        self.callback = callback

    def initalize(self):
        self.client = MQTTClient(self.id, self.broker_address)
        self.client.subscribe(self.callback)

    def connect(self):
        self.client.connect()

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    # this needs to be handled by a timer!!!
    def run(self, timer):
        try:
            self.client.check_msg()
        except OSError as e:
            print(e)
