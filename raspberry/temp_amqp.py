#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import spidev
import pika
import json
import os
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
UV_SENSOR = 1 # analog
DUMMY_SENSOR = 2 # analog
MOVEMENT_SENSOR = 4
TEMPERATURE_SENSOR = 3
TEMPERATURE_SENSOR_TYPE = Adafruit_DHT.DHT22

GPIO.setup(MOVEMENT_SENSOR, GPIO.IN)

spi = spidev.SpiDev()
spi.open(0,0)

def main():
    credentials = pika.PlainCredentials('autohome', os.environ['AMQP_PASSWORD'])
    parameters = pika.ConnectionParameters('10.0.0.12', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    while True:
        light_reading = ReadChannel(LIGHT_SENSOR)
        uv_reading = ReadChannel(UV_SENSOR)
        dummy_reading = ReadChannel(DUMMY_SENSOR)

        movement = GPIO.input(MOVEMENT_SENSOR) == 1
        humidity, temperature = Adafruit_DHT.read_retry(TEMPERATURE_SENSOR_TYPE, TEMPERATURE_SENSOR)

        print "======= reading ============"
        print "LIGHT: %d" % light_reading
        print "UV: %d" % uv_reading
        print "DUMMY: %d" % dummy_reading
        print "MOVEMENT: %d" % movement
        print "HUMIDITY: %f" % humidity
        print "TEMPERATURE: %f" % temperature

        print "======= publish ============"
        messages = [
                { 'location': 'office', 'kind': 'movement', 'state': movement },

                { 'location': 'office', 'kind': 'light', 'value': light_reading },
                { 'location': 'office', 'kind': 'uv', 'value': uv_reading },
                { 'location': 'office', 'kind': 'dummy', 'value': dummy_reading },
                { 'location': 'office', 'kind': 'humidity', 'value': humidity },
                { 'location': 'office', 'kind': 'temperature', 'value': temperature },
        ]

        for message in messages:
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
