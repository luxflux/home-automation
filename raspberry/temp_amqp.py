#!/usr/bin/env python

import os
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import spidev
import pika
import json
import signal
import sys

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

LIGHT_SENSOR = 0 # analog
# UV_SENSOR = 1 # analog
UV_SENSOR = 7 # analog
DUMMY_SENSOR = 2 # analog
MOVEMENT_SENSOR = 4
TEMPERATURE_SENSOR = 3
TEMPERATURE_SENSOR_TYPE = Adafruit_DHT.DHT22

GPIO.setup(MOVEMENT_SENSOR, GPIO.IN)

spi = spidev.SpiDev()
spi.open(0,0)

class MissingConfigVariable(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return repr("Missing ENV Variable %s" %self.name)

for variable in ['AMQP_PASSWORD', 'AMQP_USER', 'AMQP_HOST', 'LOCATION']:
    if not os.environ.has_key(variable):
        raise MissingConfigVariable(variable)

def main():
    credentials = pika.PlainCredentials(os.environ['AMQP_USER'], os.environ['AMQP_PASSWORD'])
    parameters = pika.ConnectionParameters(os.environ['AMQP_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    print >> sys.stdout, 'AMQP connection established'
    while True:
        print >> sys.stdout, 'Reading sensors'
        # light_reading = ReadChannel(LIGHT_SENSOR)
        uv_reading = ReadChannel(UV_SENSOR)
        print ReadChannel(0)
        print ReadChannel(1)
        print ReadChannel(2)
        print ReadChannel(3)
        print ReadChannel(4)
        print ReadChannel(5)
        print ReadChannel(6)
        print ReadChannel(7)
        print ReadChannel(8)
        # dummy_reading = ReadChannel(DUMMY_SENSOR)

        # movement = GPIO.input(MOVEMENT_SENSOR) == 1
        # humidity, temperature = Adafruit_DHT.read_retry(TEMPERATURE_SENSOR_TYPE, TEMPERATURE_SENSOR)

        print "======= reading ============"
        # if light_reading:
        #     print "LIGHT: %d" % light_reading
        if uv_reading:
            print "UV: %d" % uv_reading
        # if dummy_reading:
        #     print "DUMMY: %d" % dummy_reading
        # if movement:
        #     print "MOVEMENT: %d" % movement
        # if humidity:
        #     print "HUMIDITY: %f" % humidity
        # if temperature:
        #     print "TEMPERATURE: %f" % temperature

        print "======= publish ============"
        messages = [
                # { 'location': os.environ['LOCATION'], 'kind': 'movement', 'state': movement },

                # { 'location': os.environ['LOCATION'], 'kind': 'light', 'value': light_reading },
                { 'location': os.environ['LOCATION'], 'kind': 'uv', 'value': uv_reading },
                # { 'location': os.environ['LOCATION'], 'kind': 'dummy', 'value': dummy_reading },
                # { 'location': os.environ['LOCATION'], 'kind': 'humidity', 'value': humidity },
                # { 'location': os.environ['LOCATION'], 'kind': 'temperature', 'value': temperature },
        ]

        for message in messages:
            print message
            channel.basic_publish(exchange='homeauto',
                    routing_key='measurements.office', body=json.dumps(message))

        time.sleep(1)


while True:
    try:
        print >> sys.stdout, 'Starting main...'
        main()
    except pika.exceptions.ConnectionClosed:
        print >> sys.stderr, 'Retrying in 1s after ConnectionClosed'
        time.sleep(1)
        pass
