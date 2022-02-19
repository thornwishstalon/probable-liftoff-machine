from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_TRIP_START, EVENT_POST_TRIP_END, \
    EventFactory, EVENT_PRE_TRIP_START, EVENT_MOVEMENT_UPDATE, EVENT_PRE_TRIP_END, EVENT_UPDATE_FLOOR
import ubinascii
from machine import Timer, unique_id, Pin
import time

import gc

#########################################################################
### aka the MUSCLE
class MovementModule(LiftoffModule):

    def __init__(self, config):
        super().__init__(config)
        self.register = {}
        self.current_floor = 1
        self.current_transaction = None
        self.moving = False
        self.counter = 0
        self.seconds_per_floor = 4
        self.next = None
        self.direction = None

    def state(self):
        return {'currentLevel': self.current_floor}

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_PRE_TRIP_START, self.register_transaction, 500)
        subs.register(EVENT_POST_TRIP_END, self.de_register_transaction, 500)
        subs.register(EVENT_TRIP_START, self.move, 500)
        return subs

    def move(self, message):
        """
        simulate do the 'moving
        :param message:
        :return:
        """
        print('move')
        print(message)
        if not self.moving and self.current_floor != message['next']:
            self.moving = True
            self.next = message['next']
            self.direction = self.next < self.current_floor
            if self.direction:
              rotor_up()
            else:
              rotor_down()  
            

    def register_transaction(self, message):
        """
        keep track of the ongoing transactino
        :param message:
        :return:
        """
        print('register')
        print(message)
        self.current_transaction = message['id']

    def de_register_transaction(self, message):
        """
        clear current
        :param message:
        :return:
        """
        print('un_register')
        if message['id'] == self.current_transaction:
            self.current_transaction = None
        else:
            # something is wrong!!!
            pass
#########################################################################

# timers
fetch_timer = Timer(0)
measurement_timer = Timer(1)
state_timer = Timer(2)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()
config.mode = 1
module = MovementModule(config)
module.start()

# LEDS
# for pinout see ESP8266 part in doc/exports/movement_module.drawio.png
FLOOR_1 = Pin(16, Pin.OUT)
FLOOR_2 = Pin(5, Pin.OUT)
FLOOR_3 = Pin(4, Pin.OUT)
FLOOR_4 = Pin(0, Pin.OUT)
FLOOR_5 = Pin(2, Pin.OUT)
# light map:  used in light_up(light)
lights = {1: FLOOR_1, 2: FLOOR_2, 3: FLOOR_3, 4: FLOOR_4, 5: FLOOR_5}

rotor_pin = machine.Pin(14)
rotor = machine.PWM(rotor_pin)
rotor.freq(50)
rotor.duty(0)

#########################################################################
# post everybody about the current state
def publish_state(timer):
    global module
    module.mqtt.publish(
        EVENT_UPDATE_FLOOR,
        EventFactory.create_event(config.mqtt_id, module.current_transaction, module.state())
    )

def rotor_up():
  rotor.duty(10)
  
def rotor_down():
  rotor.duty(200)
  
def rotor_stop():
  rotor.duty(0)

def light_up(floor):
    for key, value in lights.items():
        value.on() if key in floor else value.off()


# simulate moving
def update_state(timer):
    global module    
    if module.moving:
        module.counter += 1
        if module.counter == module.seconds_per_floor:
            if not module.direction:
                module.current_floor += 1
            else:
                module.current_floor -= 1
            module.counter = 0
            # light up stuff
            light_up([module.current_floor])
            module.mqtt.publish(
                EVENT_UPDATE_FLOOR,
                EventFactory.create_event(config.mqtt_id, module.current_transaction, module.state())
            )
            
            if module.current_floor == module.next:
              rotor_stop()
              module.moving = False
              module.next = None
              module.direction = None
              module.mqtt.publish(
                  EVENT_PRE_TRIP_END,
                  EventFactory.create_event(
                    module.config.mqtt_id, 
                    module.current_transaction,
                    {'currentLevel': module.current_floor}
                  )
              )


###### TIMERS

print('start mqtt queue')
fetch_timer.init(period=500, mode=Timer.PERIODIC, callback=module.run)

light_up([1, 2, 3, 4, 5])
time.sleep_ms(500)
light_up([module.current_floor])
# publish current_floor to other modules
publish_state(None)
gc.collect()

#########################################################################
#########################################################################
print('start update queue')
# measurement_timer.init(period=1000, mode=Timer.PERIODIC, callback=publish_state)
state_timer.init(period=1000, mode=Timer.PERIODIC, callback=update_state)




