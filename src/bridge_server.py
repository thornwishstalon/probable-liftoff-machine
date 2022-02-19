from machine import Pin, PWM, SoftI2C, Timer, unique_id
import ubinascii
import time
import urandom

from bridge.bridge import setup_bridge
from bridge.trip import TripSchedule
from common.credentials import Config
from common.event import EVENT_UPDATE_FLOOR, EVENT_PRE_TRIP_START, EVENT_TRIP_START, EVENT_POST_TRIP_END, \
    EVENT_PRE_TRIP_END, EventFactory, EVENT_UPDATE_NEXT_QUEUE
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList

keys = 'abcdefghijklmnopqrstuvwxyz1234567890'

# LEDS
# for pinout see doc/exports/brain_module.drawio.png
GREEN = Pin(17, Pin.OUT)
YELLOW = Pin(13, Pin.OUT)
RED = Pin(12, Pin.OUT)
DOOR = Pin(14, Pin.OUT)  # -> simulate servo now

rotor_pin = Pin(2)
rotor = PWM(rotor_pin)
rotor.freq(8)

rotor.duty(0)

class BridgeStateMachine:
    READY = 0
    PREPARE_TRIP = 1
    EXECUTE_TRIP = 2
    FINISH_TRIP = 3


class DataState:
    state = BridgeStateMachine.READY
    current_floor = 0
    doors = 4
    moving = False

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def update_current_floor(self, message):
        self.current_floor = message['currentLevel']
        return True

    def open_doors(self):
        if self.doors < 4:
            self.doors += 1

    def close_doors(self):
        if self.doors > 0:
            self.doors -= 1

    @property
    def json(self):
        return {
            "state": self.state,
            "currentLevel": self.current_floor,
            "doors": self.doors,
            "moving": self.moving,
            "next": list(self.scheduler.queue.keys())
        }

    @property
    def next_queue(self):
        return {
            "next": list(self.scheduler.queue.keys())
        }


def light_ready():
    GREEN.on()
    YELLOW.off()
    RED.off()


def light_busy():
    GREEN.off()
    YELLOW.on()
    RED.off()


def light_moving():
    GREEN.off()
    YELLOW.off()
    RED.on()
    
  
door_timer = Timer(3)  
####### door control
def rotor_open():
  rotor.duty(14)
  door_timer.init(period=500, mode=Timer.ONE_SHOT, callback=lambda t:rotor.duty(0))
  

def rotor_close():
  rotor.duty(6)
  door_timer.init(period=500, mode=Timer.ONE_SHOT, callback=lambda t:rotor.duty(0))
  


### aka the BRAIN
class BridgeServer(LiftoffModule):

    def __init__(self, config, lcd=None):
        super().__init__(config, lcd)
        self.schedule = TripSchedule()
        self.data_state = DataState(self.schedule)
        self.transaction_code = ""

        self.max_wait_cycles = 6
        self.wait_cycles = self.max_wait_cycles

    def is_done_waiting(self):
        self.wait_cycles -= 1

        if self.wait_cycles % 2 == 0:
            GREEN.off()
        else:
            GREEN.on()

        if self.wait_cycles == 0:
            self.wait_cycles = self.max_wait_cycles
            return True
        return False

    def update_state(self, timer):

        if self.data_state.state == BridgeStateMachine.READY:
            light_ready()

            if self.schedule.has_trip_scheduled() and self.is_done_waiting():
                self.data_state.state = BridgeStateMachine.PREPARE_TRIP
                self.transaction_code = BridgeServer.generate_code()

        elif self.data_state.state == BridgeStateMachine.PREPARE_TRIP:
            light_busy()
            if self.data_state.doors == 4:
                rotor_close()
                self.mqtt.publish(
                    EVENT_PRE_TRIP_START,
                    EventFactory.create_event(
                        self.config.mqtt_id,
                        self.transaction_code,
                        {}
                    )
                )
                self.data_state.close_doors()
            elif self.data_state.doors > 0:
                self.data_state.close_doors()
            elif self.data_state.doors == 0:
                DOOR.on()
                
                self.data_state.state = BridgeStateMachine.EXECUTE_TRIP

        elif self.data_state.state == BridgeStateMachine.EXECUTE_TRIP:
            light_moving()
            if not self.data_state.moving:
                self.data_state.moving = True
                self.mqtt.publish(
                    EVENT_TRIP_START,
                    EventFactory.create_event(
                        self.config.mqtt_id,
                        self.transaction_code,
                        {"next": self.schedule.get_next_trip(self.data_state.current_floor)}
                    )
                )

        elif self.data_state.state == BridgeStateMachine.FINISH_TRIP:
            light_busy()
            if self.data_state.doors == 0:          
                self.mqtt.publish(
                    EVENT_POST_TRIP_END,
                    EventFactory.create_event(
                        self.config.mqtt_id,
                        self.transaction_code,
                        {}
                    )
                )
                self.data_state.open_doors()
            elif self.data_state.doors < 4:
                self.data_state.open_doors()
            elif self.data_state.doors == 4:
                rotor_open()
                DOOR.off()                
                self.data_state.state = BridgeStateMachine.READY
                self.data_state.moving = False

    @classmethod
    def generate_code(cls):
        return ''.join((urandom.choice(keys) for _ in range(8)))

    def arrive(self, message):
        self.data_state.state = BridgeStateMachine.FINISH_TRIP
        self.data_state.current_floor = message['currentLevel']
        self.data_state.scheduler.delete_from_queue(message['currentLevel'])
        self.mqtt.publish(
            EVENT_UPDATE_NEXT_QUEUE,
            EventFactory.create_event(
                self.config.mqtt_id,
                self.transaction_code,
                self.data_state.next_queue
            )
        )

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
gc_timer = Timer(2)


#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()
# open up
rotor_open()

module = BridgeServer(config, lcd=lcd)
module.start()
print('network setup done')



web = setup_bridge(module)  

###### TIMERS
fetch_timer.init(period=250, mode=Timer.PERIODIC, callback=module.run)
state_timer.init(period=500, mode=Timer.PERIODIC, callback=module.update_state)

## run server
web.run(debug=True, host=module.host, port=80)

import gc


state_timer.init(period=60000, mode=Timer.PERIODIC, callback=lambda t: gc.collect())



