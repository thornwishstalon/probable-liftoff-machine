from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_POST_TRIP_END, EventFactory, EVENT_PRE_TRIP_START, EVENT_POWER_UPDATE, \
    EVENT_POWER_TRACK_DONE
import ubinascii
from machine import Timer, unique_id
import time
import urandom


### aka the NOSE
class PowerModule(LiftoffModule):

    def __init__(self, config):
        super().__init__(config)
        self.register = {}
        self.power = 0.

    def state(self):
        return {'power': self.power}

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_PRE_TRIP_START, self.start_track, 500)
        subs.register(EVENT_POST_TRIP_END, self.stop_track, 500)
        return subs

    def start_track(self, message):
        """
        start recording
        :param message:
        :return:
        """
        # todo: check if we don't overwrite a current state!
        transaction_code = message['id']
        self.register[transaction_code] = {'power': 0., 'time_ms': 0}

    def stop_track(self, message):
        """
        transaction has ended: clear the track and report the total consumption to the broker!
        :param message:
        :return:
        """
        transaction_code = message['id']
        record = self.register[transaction_code]

        module.mqtt.publish(
            EVENT_POWER_TRACK_DONE,
            EventFactory.create_event(config.mqtt_id, transaction_code, record)
        )
        # remove record
        del self.register[transaction_code]

    def update_register(self, power, interval_ms):
        """
        update all active transaction tracks with latest power measurement
        :param power:
        :param interval_ms:
        :return:
        """
        # for all active transactions, add the consumption, and the interval count respectively
        if len(self.register) > 0:
            for item in self.register.values():
                item['power'] += power
                item['time_ms'] += interval_ms


# timers
fetch_timer = Timer(0)
measurement_timer = Timer(1)
publish_timer = Timer(2)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()

module = PowerModule(config)
module.start()


# post everybody about the current state
def publish_state(timer):
    global module
    if module.mqtt:
        module.mqtt.publish(
            EVENT_POWER_UPDATE,
            # transaction id is None, because it's a general event
            EventFactory.create_event(config.mqtt_id, None, module.state())
        )


def measure_power(timer):
    # todo actual measure something:
    current_power = urandom.getrandbits(5)
    global module
    module.power = current_power
    # update ongoing transaction sums with latest measurement
    module.update_register(current_power, 250)


###### TIMERS
print('start mqtt queue')
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
time.sleep_ms(500)
print('start update queue')
publish_timer.init(period=1000, mode=Timer.PERIODIC, callback=publish_state)
publish_timer.init(period=250, mode=Timer.PERIODIC, callback=measure_power)
