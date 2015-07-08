#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from influxdb.influxdb08 import InfluxDBClient

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

uv_sensor = 14
movement_sensor = 15
temperature_sensor_pin = 18
temperature_sensor_type = Adafruit_DHT.DHT22

GPIO.setup(uv_sensor, GPIO.IN)
GPIO.setup(movement_sensor, GPIO.IN)
#GPIO.setup(temperature_sensor, GPIO.IN)

while True:
    #uv_reading = GPIO.input(uv_sensor)
    movement = GPIO.input(movement_sensor)
    humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor_type, temperature_sensor_pin)

    #print "UV: %d" % uv_reading
    print "MOVEMENT: %d" % movement
    print "HUMIDITY: %f" % humidity
    print "TEMPERATURE: %f" % temperature

    json_body = [{
        "points": [
	  [movement, humidity, temperature],
        ],
        "name": "office",
        "columns": ["movement", "humidity", "temperature"],
    }]

    client = InfluxDBClient(host='influx01.yux.ch', port=8086, username='homeuser', password='homepw', database='homedb')
    client.write_points(json_body)

    time.sleep(1)

GPIO.cleanup()
