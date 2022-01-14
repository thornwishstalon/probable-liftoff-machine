# probable-liftoff-machine
UbiComp WS 2021 - Group 10

## module server
props to https://github.com/anson-vandoren/esp8266-captive-portal
but a lot has changed....

## how to run stuff
### bridge aka the BRAIN
* run `setup_bridge.py` with proper wifi credentials
* copy all files from``module`` and `bridge` modules to the board (create respective directories on the board!)
* copy the config file (`config.creds`) from `/config/bride/` to the root level of the board
* run `bridge_server.py`
  + this will start an access point with ssid `liftoff` 
  + connect with the machin that runs the mqtt broker to this wifi
  + mqtt broker needs to run on `192.168.4.2`!!!!!

### run the rest
...
## web interface

you will need [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)

run:
```
docker-compose up
```

and goto [http://localhost:8080](http://localhost:8080)

