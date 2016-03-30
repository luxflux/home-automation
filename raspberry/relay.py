#!/usr/bin/env python

import os
import RPi.GPIO as GPIO
import time
import spidev
import signal
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0,0)

def send_state(port, state):
    print "%d to port %d" % (state, port)
    GPIO.output(port, state)

send_state(4, 1)
time.sleep(1)
send_state(3, 1)
time.sleep(1)
send_state(2, 1)
time.sleep(1)
send_state(16, 1)
time.sleep(1)

send_state(4, 0)
time.sleep(1)
send_state(3, 0)
time.sleep(1)
send_state(2, 0)
time.sleep(1)
send_state(16, 0)
time.sleep(1)
