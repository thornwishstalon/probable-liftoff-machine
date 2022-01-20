from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_TRIP_READY, EVENT_POST_TRIP_END, \
    EventFactory, EVENT_PRE_TRIP_START, EVENT_MOVEMENT_UPDATE, EVENT_PRE_TRIP_END
import ubinascii
from machine import Timer, unique_id
import time

### aka the MUSCLE
class MovementModule(LiftoffModule):

    def __init__(self, config):
        super().__init__(config)
        self.register = {}
        self.current_floor = 0
        self.current_transaction = None

    def state(self):
        return {'current_floor': self.current_floor}

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_PRE_TRIP_START, self.register_transaction, 500)
        subs.register(EVENT_POST_TRIP_END, self.de_register_transaction, 500)
        subs.register(EVENT_TRIP_READY, self.move, 500)
        return subs

    def move(self, message):
        """do the 'moving'"""
        print(message)
        # todo: add code and trigger other events accordingly e.g.   

        # mark that you have arrived by publishing this EVENT_PRE_TRIP_END!
        self.mqtt.publish(
            EVENT_PRE_TRIP_END,
            EventFactory.create_event(self.config.mqtt_id, self.current_transaction, {}).json
        )

    def register_transaction(self, message):
        # todo: check if we don't overwrite a current state!
        self.current_transaction = message['id']

    def de_register_transaction(self, message):
        self.current_transaction = None


# timers
fetch_timer = Timer(0)
measurement_timer = Timer(1)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()

module = MovementModule(config)
module.start()


# post everybody about the current state
def publish_state(timer):
    global module
    if module.mqtt:
        module.mqtt.publish(
            EVENT_MOVEMENT_UPDATE,
            EventFactory.create_event(config.mqtt_id, module.current_transaction, module.state()).json
        )


###### TIMERS
print('start mqtt queue')
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
time.sleep_ms(500)
print('start update queue')
measurement_timer.init(period=1000, mode=Timer.PERIODIC, callback=publish_state)
