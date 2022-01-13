from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_TRIP_READY, EVENT_POST_TRIP_START, EVENT_PRE_TRIP_END, EVENT_TRIP_END, \
    EVENT_POST_TRIP_END
import ubinascii
from machine import Timer, unique_id


class MovementModule(LiftoffModule):

    def __init__(self, config, essid=None):
        super().__init__(config, essid)
        self.current_floor = 0

    def floor(self):
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
        return

# timers
fetch_timer = Timer(0)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id)

module = MovementModule(config)
module.start()

###### TIMERS
fetch_timer.init(period=100, mode=Timer.PERIODIC, callback=module.mqtt.run)
