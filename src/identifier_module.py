from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_POST_TRIP_END, EventFactory, EVENT_PRE_TRIP_START, EVENT_POWER_UPDATE, \
    EVENT_POWER_TRACK_DONE, EVENT_ID_CHECK
import ubinascii
from machine import Timer, unique_id
import time
import urandom


### aka the EYES
class IdentifierModule(LiftoffModule):

    def __init__(self, config):
        super().__init__(config)

        # pseudo ids
        self.ids = [
            'alpha'
            'beta',
            'gamma',
            'delta',
            'epsilon',
            'zeta',
            'eta'
            'theta'
        ]

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_PRE_TRIP_START, self.post_ids, 500)
        return subs

    def post_ids(self, message):
        transaction_code = message['id']
        record = self.catch_ids()

        module.mqtt.publish(
            EVENT_ID_CHECK,
            EventFactory.create_event(config.mqtt_id, transaction_code, record).json
        )

    def catch_ids(self):
        # push random ids
        passengers = []
        # at least 1
        passengers.append(self.ids[urandom.getrandbits(3)])
        while urandom.getrandbits(1) == 1:
            passengers.append(self.ids[urandom.getrandbits(3)])

        return {'passengers': passengers}


# timers
fetch_timer = Timer(0)
measurement_timer = Timer(1)
publish_timer = Timer(2)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()

module = IdentifierModule(config)
module.start()

###### TIMERS
print('start mqtt queue')
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
time.sleep_ms(500)
