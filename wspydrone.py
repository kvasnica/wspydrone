# WSPYDRONE: websocket gateway to python-ardrone (https://github.com/venthur/python-ardrone)
#
# Copyright (C) 2016 Michal Kvasnica <michal.kvasnica@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# git clone https://github.com/venthur/python-ardrone.git
# pip install websocket-client
# pip3 install websocket-client

import websocket
import threading
import time
import libardrone
import json
import logging

# assumes the SWSB broker is running locally at port 8025
# (see https://github.com/kvasnica/swsb)
WS_URL = "ws://127.0.0.1:8025/t/ardrone"

SamplingTime = 0.5 # in seconds
MinimalSampling = 0.05 # minimal sampling time for mesurements
Running = False
drone = libardrone.ARDrone()

logging.basicConfig(
format='[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s: %(message)s', level=logging.ERROR)
logger = logging.getLogger('wspydrone')
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

def trim_float(x, lb, ub):
	# trims "x" to the interval [lb..ub]
	return min(max(x, lb), ub)

def on_message(ws, message):
	# Message must be a json-encoded dict:
	#   {"command": "CMD", "args": ARGS}
	# Supported commands:
	#   takeoff
	#   land
	#   halt
	#   reset
	#   hover
	#   trim
	#   ping (replies with {'ping':'pong'})
	# Commands with arguments:
	#   set_speed [-1..1] as float
	#   set_sampling [0..Inf] as float
	#   move [lr, rb, vv, va] as a 1x4 array of floats
	#     lr = left-right tilt [-1..1]
	#     rb = front-back tilt [-1..1]
	#     vv = vertical speed [-1..1]
	#     va = angular speed [-1..1]
	msg = json.loads(message)
	command = msg["command"]
	if command=="ping":
		ws.send(json.dumps({'ping':'pong'}))
	elif command=="takeoff":
		drone.takeoff()
	elif command=="land":
		drone.land()
	elif command=="halt":
		drone.halt()
	elif command=="reset":
		drone.reset()
	elif command=="hover":
		drone.hover()
	elif command=="move":
		args = msg["args"]
		# trim inputs to [-1..1] range
		lr = trim_float(float(args[0]), -1, 1)
		rb = trim_float(float(args[1]), -1, 1)
		vv = trim_float(float(args[2]), -1, 1)
		va = trim_float(float(args[3]), -1, 1)
		drone.move(lr, rb, vv, va)
	elif command=="trim":
		drone.trim()
	elif command=="set_speed":
		v = trim_float(float(msg["args"]), -1, 1)
		drone.set_speed(v)
	elif command=="set_sampling":
		# sets the sampling time of the measurements
		global SamplingTime
		global MinimalSampling
		MaximalSampling = 1000
		SamplingTime = trim_float(float(msg["args"]), MinimalSampling, MaximalSampling)
		logger.debug("New sampling: %f" % SamplingTime)
	else:
		logger.error("Unrecognized command %s!" % command)
	logger.debug(message)

def on_error(ws, error):
    logger.error(error)

def on_close(ws):
	global Running
	logger.info("Drone is landing (wait 4 seconds)...")
	Running = False
	drone.land()
	time.sleep(3)
	drone.halt()
	time.sleep(1)
	logger.info("### bye ###")

def on_open(ws):
	def run(*args):
		# boadcasts navdata[0] to the websocket as a json-encoded dictionary
		#  navdata[0] = {'phi': 0, 'psi': -33, 'num_frames': 0, 'battery': 20,
		#                'altitude': 0, 'ctrl_state': 131072,
		#                'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'theta': 0}
		global SamplingTime
		global Running
		if Running:
			threading.Timer(SamplingTime, run).start()
			data = drone.navdata[0]
			logger.debug(data)
			ws.send(json.dumps(data))
	global Running
	logger.info("Websocket connected...")
	Running = True
	run()

if __name__ == "__main__":
	print('wspydron listening at %s' % WS_URL)
	logger.info("Sampling time for measurements: %f" % SamplingTime)
	ws = websocket.WebSocketApp(WS_URL,
		on_message = on_message,
		on_error = on_error,
		on_close = on_close)
	ws.on_open = on_open
	ws.run_forever()
