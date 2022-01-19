# probable-liftoff-machine 🚀
## UbiComp WS 2021 - Group 10

## TODO 👋
* [x] check if station mode works when connect to an existing wifi   
  * [x] relevant for modules connecting to the control-server
  * [x] wifi `password` should be optional! 
* [x] implement state machine for control server (and state update loop)
  * basically when to do what and wait for something
* [ ] do we need a "heartbeat" mqtt event ? 
  * [ ] implement modules:
    * callbacks & state etc
    * hardware
* [ ] implement web UI
  * bridge offers `/state` endpoint to retrieve current state
    * GET returns json representation of the bridge's state
    ```
      {
       "doors": 4,        // 4 is fully open, 0 is fully closed
       "moving": false,   //
       "state": 0,        // state value... see below!
       "current_floor": 0 //
      }
    ```
    ```
    // internal states
         READY = 0
         PREPARE_TRIP = 1
         EXECUTE_TRIP = 2
         FINISH_TRIP = 3
    ```
  * bridge offers `/floor`
    * GET returns the current floor it's on
    * PUT with `next` parameter will schedule a trip to `next`'s value

## external projects used:

### https://github.com/anson-vandoren/esp8266-captive-portal
props to this project for the wifi setup stuff.

but a lot has been changed in the end. good start point though!

### https://github.com/deviantony/docker-elk
all elastic, logstash, kibana related. 

## Architecture
meet the MAELK Stack 🍻

![arch](https://github.com/thornwishstalon/probable-liftoff-machine/blob/main/doc/exports/components.drawio.png?raw=true)


## DOCKER 🐳

you will need [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)

to run:
 * `apache` for the UI - http://localhost:8080
 * `mosquitto` the MQTT broker - http://localhost:1883
 * `kibana`  http://localhost:5601
 * `elasticsearch`
 * `logstash` - logstash will push every mqtt message from all topics into `elastic`'s `logstash`-search index ;)

see `docker-compose.yml` for more information or the respective Docker files and configs.

## how things work together 🔥
* one unit serves as wifi access point and control server
* a machine running `mosquitto` (MQTT Broker) needs to connect to this network
* communication between all modules occur via MQTT through this broker
* the control server runs a webserver that can be used for interaction
  * http as the public interface 
  * interacting with the system and getting information
* commands can be issued directly publishing mqtt messages to certain topics

### Liftoff Module Framework
we have built a common codebase to be used for all parts of this project -> `src/module/liftoff_module.py`
any class extending `LiftoffModule` will be capable to either create a wifi or connect to an existing, build a connection to a MQTT Broker and provide the means to react to MQTT topics or push topics themself.

let's explain this modularity with the movement module: 

```python
from common.credentials import Config
from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from common.event import EVENT_MOVEMENT_UPDATE,EVENT_TRIP_READY,EVENT_POST_TRIP_START,EVENT_POST_TRIP_END
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

    # any module needs to implement the subscriber function! The subscriber list 
    # is used to call callbacks if a message for the defined topic is received via mqtt 
    @property   
    def subscriber(self):
        subs = SubscriberList()
        # 
        subs.register(
            EVENT_TRIP_READY,   # topic name 
            self.move,          # callback
            500                 # callback priority, if multiple callbacks register to the same topic
                                # priority is used to define the order in which they are called
        )
        # always return the Subscriber LIST!!!!
        return subs

    # the callback function, which will get executed when a message for EVENT_TRIP_READY is received
    def move(self, message):
        # push a new event
        self.mqtt.publish(EVENT_POST_TRIP_START, b"0")
        # do stuff
        # here we just increase the current_floor by 1, we could also do something with the 'message' 
        # (it's a byte string so be careful if you want to have numerical values!)
        self.current_floor +=  1
        # push another event after we did things
        self.mqtt.publish(EVENT_POST_TRIP_END, b"0")
        


### timers
# the fetch timer will be used to get waiting messages in the mqtt queue
fetch_timer = Timer(0)

# this timer will be used to push the current state of this module to whoever is interested
measurement_timer = Timer(1)

# the client id is used to identify this module at the mqtt broker
client_id = ubinascii.hexlify(unique_id())
# this will load config from the config.creds file!
config = Config(client_id).load()

module = MovementModule(config)
# start() will create a new wifi or connect to an existing one depending on the wifi config in the creds-file
# then a connection to the mqtt broker is created and we will subscribe to all topics listed 
# in the module's subscribe function. in this example it's 'EVENT_TRIP_READY', which will get handled by move()
module.start()

# this timer callback will get used to just publish the current state to the broker every second.
def publish_state(timer):
  global module
  if module.mqtt:
    # let's push the data from state() to the broker ;) => {'current_floor': self.current_floor}
    module.mqtt.publish(EVENT_MOVEMENT_UPDATE, ujson.dumps(module.state()))  

###### TIMERS
print('start mqtt queue')
fetch_timer.init(period=1000, mode=Timer.PERIODIC, callback=module.run)
time.sleep_ms(500)

print('start update queue')
measurement_timer.init(period=1000, mode=Timer.PERIODIC, callback=publish_state)

## THE END
```



### MQTT (https://mqtt.org/)
#### install mosquitto on osx with homebrew
`$ brew install mosquitto`

with the broker runnning in the container:

subscribe to a topic: (this is a blocking command) - default port is `1883` 

`$ mosquitto_sub -h localhost -t liftoff.update.floor`

publish topics in a separate shell:

`$ mosquitto_pub -h localhost  -t liftoff.update.floor -m 1`
 

#### mqtt explorer - all platforms
looks promising: http://mqtt-explorer.com/


## how to run stuff ⚡️
### bridge aka the BRAIN @ESP32
* run `setup_bridge.py` with proper wifi credentials
  * this will install all the dependencies 
* copy all files from `module`, `common` and `bridge` modules to the board (create respective directories on the board!)
* copy the config file (`config.creds`) from `/config/bride/` to the root level of the board
* run `bridge_server.py`
  + this will start an access point with ssid `liftoff` 
    + further setup steps will wait until the mqtt-broker is available. so before starting other boards first connect your machine, that runs the broker to the network!
  + connect with the machin that runs the mqtt broker to this wifi
  + now mqtt broker is available at `192.168.4.2`
  + ESP32's display should say: `mqtt ready`
  + the webserver should be ready now
    + http://192.168.4.1/floor should show 0 as current floor
    + change the floor by publishing a new floor to `liftoff.update.floor`
      + e.g. `$ mosquitto_pub -h localhost  -t liftoff.update.floor -m 1`
    + now current floor should be 1
  + et voilà 🎉
  

### run the rest of the modules (movement, power or rfid)
* run `setup_module.py` with proper wifi credentials
  * this will install all the dependencies 
* copy all files from``module`` and  `common` modules to the board (create respective directories on the board!)
* create a config file (`config.creds`) at the root level of the board
  * at least set the `ssid` and `mqtt_broker`!!! 
* start the respective main file (e.g.: `movement_module.py`)
  * the module will try to connect to defined wifi (from the `config.creds`file)
  * then connect to the mqtt broker
  * and register all mqtt topics the module is interested in
  * and finally starts a periodic push of state topics to the broker - as part of a periodic timer function 
+ that's it

### config file aka config.creds

the config file should look like this:
```
{
  "ssid": "liftoff",            # the ssid of the wifi you want to connect to 
  "password": "<password>",     # [optional] the password for that wifi. can be optional if it's an open wifi
  "mqtt_broker": "192.168.4.2", # the IP or host-name where the mqtt-broker is running 
  "broker_password": "<pwd>",   # [optional] mqtt broker password
}
```
`broker_password` is not used at the moment!

## Analytics and Monitoring

run to spin up all the necessary containers:
```
docker-compose up
```

if you have changed Dockerfiles you will need to rebuild the images: add the `--build` flag

### KIBANA
-> the UI to discover stuff in `elasticsearch`

goto [http://localhost:5601](http://localhost:5601)

```
user: elastic
password: changeme
```
if you access kibana for the first time, you will be asked to create an index_pattern
```
logstash*
```
will be fine and select ``@timestamp`` as datetime thing.

then click the menu-icon at the top-left corner and go to `Analytics`/`Discover` and see all the stuff happining! 



### web interface

you will need [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)



and goto [http://localhost:8080](http://localhost:8080)

