from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_MOVEMENT_STATE,EVENT_TRIP_READY,EVENT_POST_TRIP_START,EVENT_POST_TRIP_END
import ubinascii
from machine import Timer, unique_id
import ujson
import time

class MovementModule(LiftoffModule):

    def __init__(self, config):
        super().__init__(config)
        self.current_floor = 0

    def state(self):
        return {'current_floor': self.current_floor}

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_TRIP_READY, self.move, 500)
        return subs

    def move(self, message):
        """do the 'moving'"""
        print(message)
        # todo: add code and trigger other events accordingly e.g.   
        self.mqtt.publish(EVENT_POST_TRIP_START, b"0")
        self.current_floor +=  1
        self.mqtt.publish(EVENT_POST_TRIP_END, b"0")
        


# timers
fetch_timer = Timer(0)
measurement_timer = Timer(1)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()

module = MovementModule(config)
module.start()

module.run(None)
time.sleep_ms(500)
module.run(None)

#
def publish_state(timer):
  global module
  if module.mqtt:
    module.mqtt.publish(EVENT_MOVEMENT_STATE, ujson.dumps(module.state()))  

###### TIMERS
print('start mqtt queue')
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
time.sleep_ms(500)
print('start update queue')
measurement_timer.init(period=1000, mode=Timer.PERIODIC, callback=publish_state)


