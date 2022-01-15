# probable-liftoff-machine 🚀
## UbiComp WS 2021 - Group 10

## TODO 👋
* check if station mode works when connect to an existing wifi
  * relevant for modules connecting to the control-server
* implement state machine for control server (and state update loop)
  * basically when to do what and wait for something 
* implement modules:
  * callbacks & state etc
  * hardware
* implement web UI

## module server
props to https://github.com/anson-vandoren/esp8266-captive-portal for the wifi setup stuff

but a lot has changed....

## DOCKER 🐳

you will need [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)

to run:
 * `apache` for the UI - http://localhost:8080
 * `mosquitto` the MQTT broker - http://localhost:1883

see `docker-compose.yml`

## how things work together 🔥
* one unit serves as wifi access point and control server
* a machine running `mosquitto` (MQTT Broker) needs to connect to this network
* communication between all modules occur via MQTT through this broker
* the control server runs a webserver that can be used for interaction
  * http as the public interface 
  * interacting with the system and getting information
* commands can be issued directly publishing mqtt messages to certain topics

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
* copy all files from``module`` and `bridge` modules to the board (create respective directories on the board!)
* copy the config file (`config.creds`) from `/config/bride/` to the root level of the board
* run `bridge_server.py`
  + this will start an access point with ssid `liftoff` 
    + further setup steps will wait until the mqtt-broker is available. so before starting other boards first connect your machine, that runs the broker to the network!
  + connect with the machin that runs the mqtt broker to this wifi
  + now mqtt broker is available at `192.168.4.2`
  + ESP32's display should say: `mqtt ready`



### run the rest
... TODO


## web interface

you will need [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)

run:
```
docker-compose up
```

and goto [http://localhost:8080](http://localhost:8080)

