from machine import Pin, SoftI2C, Timer, unique_id
import ubinascii
import time
import urandom

from bridge.bridge import setup_bridge
from bridge.trip import TripSchedule
from common.credentials import Config
from common.event import EVENT_UPDATE_FLOOR, EVENT_PRE_TRIP_START, EVENT_TRIP_START, EVENT_POST_TRIP_END, EventPayload, \
    EVENT_PRE_TRIP_END
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList

keys = 'abcdefghijklmnopqrstuvwxyz1234567890'


class BridgeStateMachine:
    READY = 0
    PREPARE_TRIP = 1
    EXECUTE_TRIP = 2
    FINISH_TRIP = 3


class DataState:
    current_floor = 0
    doors = 0

    def update_current_floor(self, message):
        self.current_floor = int(message)
        return True

    def open_doors(self):
        self.doors = 1

    def close_doors(self):
        self.doors = 0


class BridgeServer(LiftoffModule):

    def __init__(self, config, lcd=None):
        super().__init__(config, lcd)
        self.data_state = DataState()
        self.schedule = TripSchedule()
        self.state = BridgeStateMachine.READY
        self.transaction_code = ""

    def update_state(self, timer):
        if self.state == BridgeStateMachine.READY:
            if self.schedule.has_trip_scheduled():
                self.state = BridgeStateMachine.PREPARE_TRIP
                self.transaction_code = BridgeServer.generate_code()

        elif self.state == BridgeStateMachine.PREPARE_TRIP:
            if self.data_state.doors == 0:
                self.mqtt.publish(EVENT_PRE_TRIP_START, EventPayload(self.transaction_code, {}).json)
                self.data_state.close_doors()
            else:
                self.state = BridgeStateMachine.EXECUTE_TRIP

        elif self.state == BridgeStateMachine.EXECUTE_TRIP:
            self.mqtt.publish(
                EVENT_TRIP_START,
                EventPayload(self.transaction_code,
                             {"next": self.schedule.pop_trip(self.data_state.current_floor)}).json
            )

        elif self.state == BridgeStateMachine.FINISH_TRIP:
            self.data_state.open_doors()
            self.mqtt.publish(
                EVENT_POST_TRIP_END,
                EventPayload(self.transaction_code, {}).json
            )
            self.state = BridgeStateMachine.READY

    @classmethod
    def generate_code(cls):
        return ''.join((urandom.choice(keys) for _ in range(8)))

    def arrive(self):
        self.state = BridgeStateMachine.FINISH_TRIP

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_UPDATE_FLOOR, self.data_state.update_current_floor, 500)
        subs.register(EVENT_PRE_TRIP_END, self.arrive, 500)

        return subs


time.sleep_ms(500)
import ssd1306

# display
i2c_rst = Pin(16, Pin.OUT)
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1)

i2c_sc1 = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)

i2c = SoftI2C(scl=i2c_sc1, sda=i2c_sda)
lcd = ssd1306.SSD1306_I2C(128, 64, i2c)

# timers
fetch_timer = Timer(0)
state_timer = Timer(1)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()

module = BridgeServer(config, lcd=lcd)
module.start()
print('network setup done')

web = setup_bridge(module)

###### TIMERS
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
state_timer.init(period=500, mode=Timer.PERIODIC, callback=module.update_state)

## run server
web.run(debug=True, host=module.host, port=80)
