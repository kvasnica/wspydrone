# wspydrone
Websocket gateway to [python-ardrone](https://github.com/venthur/python-ardrone) for AR.Drone firmware 1.5.1


## Building locally
```
pip install websockets
```

## Build for Docker
```
docker build -t kvasnica/wspydrone .
```

## Run locally

Start the simple websocket broker locally on port 8025:
```
docker run -it -p 8025:8025 kvasnica/swsb
```

Then:
```
python wspydrone
```

## Run via Docker
Start the simple websocket broker locally on port 8025:
```
docker run -it -p 8025:8025 kvasnica/swsb
```
Start the gateway:
```
docker run -it --net=host kvasnica/wspydrone
```

Note: make sure to use `--net=host` since Docker needs to connect to the drone via host's wifi.

## Usage

Connect your websocket client to `ws://127.0.0.1:8025/t/ardrone` and start sending commands and receiving navdata.

Commands must be transmitted as a json-encoded dictonary `{"command":"CMD", "args": ARGS}`

Supported commands without arguments:
* `halt`
* `hover`
* `land`
* `reset`
* `takeoff`
* `trim`
* `ping` (replies with `{'ping':'pong'}`)

Commands with arguments:
* `set_speed`: `ARGS` must be a float in the interval -1..1
* `set_sampling`: `ARGS` must be a float in the interval 0..Inf - this sets the transmission rate of measurements
* `move`: `ARGS` must be a 1x4 array of floats -1..1 \[lr, rb, vv, va\]
	* `lr`: left-right tilt speed
	* `rb`: font-back tilt speed
	* `vv`: vertical speed
	* `va`: angular speed

Note: the input data will be automatically trimmed to the required interval.

The gateway transmits back `navdata[0]` as provided by `libardrone.py`

Sample command:
```
{"args":[-0.5,0,0,0],"command":"move"}
```

Sample response:
```
{'phi': 0, 'psi': -33, 'num_frames': 0, 'battery': 20, 'altitude': 0, 'ctrl_state': 131072, 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'theta': 0}
```


## License

This software is published under the terms of the MIT License:

http://www.opensource.org/licenses/mit-license.php
