from machine import Pin,SoftI2C, Timer, unique_id
import ubinascii
import time
from bridge.bridge import setup_bridge
from common.credentials import Config
from common.event import EVENT_UPDATE_FLOOR
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
import socket


class DataState:
    current_floor = 0

    def update_current_floor(self, message):        
        self.current_floor = int(message)
        return True


class BridgeServer(LiftoffModule):
    state = DataState()
        
    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_UPDATE_FLOOR, self.state.update_current_floor, 500)
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
lcd= ssd1306.SSD1306_I2C(128,64,i2c)



# timers
fetch_timer = Timer(0)

#
client_id = ubinascii.hexlify(unique_id())
config = Config(client_id).load()


module = BridgeServer(config,lcd=lcd)
module.start()
print('network setup done')

web = setup_bridge(module)

###### TIMERS
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)

## run server
web.run(debug=True, host=module.host, port=80)


