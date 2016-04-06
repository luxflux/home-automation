#!/usr/bin/env python

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

for port in range(2, 27):
    GPIO.setup(port, GPIO.IN)


while True:
    # for port in range(2, 27):
    print "################"
    for port in [2,3,4,14,16]:
        print "Port %s: %s" % (port, GPIO.input(port))
    time.sleep(1)
