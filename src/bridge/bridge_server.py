from machine import Timer, unique_id
import ubinascii

from bridge.bridge import setup_bridge
from common.credentials import Config
from common.event import EVENT_UPDATE_FLOOR
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList

class DataState:
    current_floor:int = 0

    def update_current_floor(self, message):
        self.current_floor = message


class BridgeServer(LiftoffModule):
    state = DataState()

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_UPDATE_FLOOR, self.state.update_current_floor, 500)
        return subs



# timers
fetch_timer = Timer(0)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id)

module = BridgeServer(config)
module.start()

web = setup_bridge(module)

###### TIMERS
fetch_timer.init(period=100, mode=Timer.PERIODIC, callback=module.mqtt.run)

## run server
web.start()