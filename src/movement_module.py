from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_TRIP_READY, EVENT_POST_TRIP_END, \
    EventFactory, EVENT_PRE_TRIP_START, EVENT_MOVEMENT_UPDATE, EVENT_PRE_TRIP_END, EVENT_UPDATE_FLOOR
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
        self.moving = False
        self.counter = 0
        self.seconds_per_floor = 4
        self.next = None
        self.direction = None

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
        """
        simulate do the 'moving
        :param message:
        :return:
        """
        if self.moving == False:
            print(message)
            # todo: add code and trigger other events accordingly e.g.
            self.moving = True
            self.next = message['next']
            self.direction = self.next < self.current_floor

    def register_transaction(self, message):
        """
        keep track of the ongoing transactino
        :param message:
        :return:
        """
        self.current_transaction = message['id']

    def de_register_transaction(self, message):
        """
        clear current
        :param message:
        :return:
        """
        if message['id'] == self.current_transaction:
            self.current_transaction = None
        else:
            # something is wrong!!!
            pass


# timers
fetch_timer = Timer(0)
measurement_timer = Timer(1)
state_timer = Timer(2)

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
            EventFactory.create_event(config.mqtt_id, module.current_transaction, module.state())
        )

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
            if module.current_floor == module.next:
                module.moving = False
                module.next = None
                module.direction = None
                module.mqtt.publish(
                    EVENT_PRE_TRIP_END,
                    EventFactory.create_event(module.config.mqtt_id, module.current_transaction, {'currentLevel': module.current_floor})
                )


###### TIMERS
print('start mqtt queue')
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
time.sleep_ms(500)
print('start update queue')
measurement_timer.init(period=1000, mode=Timer.PERIODIC, callback=publish_state)
state_timer.init(period=1000, mode=Timer.PERIODIC, callback=update_state)

