#!/usr/bin/env python

import sys
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

def send_state(port, state):
    print "%d to port %d" % (state, port)
    GPIO.output(port, state)

PORT_MAPPING = {
          '1': 4,
          '2': 3,
          '3': 2,
          '4': 16,
        }

STATE_MAPPING = {
        'on': 1,
        'off': 0,
        }

port = sys.argv[1]
port = PORT_MAPPING[port]
state = sys.argv[2]
state = STATE_MAPPING[state]

send_state(port, state)

time.sleep(1)

GPIO.cleanup()
