#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import json
import pika

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
    print "read movement..."
    movement = GPIO.input(movement_sensor) == 1
    print "read humidity and temperature..."
    humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor_type, temperature_sensor_pin)

    #print "UV: %d" % uv_reading
    print "MOVEMENT: %d" % movement
    print "HUMIDITY: %f" % humidity
    print "TEMPERATURE: %f" % temperature


    print "publish..."
    connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.154'))
    channel = connection.channel()

    message = { 'location': 'office', 'kind': 'movement', 'value': movement }
    channel.basic_publish(exchange='measurements',
            routing_key='office.movement', body=json.dumps(message))

    message = { 'location': 'office', 'kind': 'humidity', 'value': humidity }
    channel.basic_publish(exchange='measurements',
            routing_key='office.humidity', body=json.dumps(message))

    message = { 'location': 'office', 'kind': 'temperature', 'value': temperature }
    channel.basic_publish(exchange='measurements',
            routing_key='office.temperature', body=json.dumps(message))
    connection.close()

#    time.sleep(1)

GPIO.cleanup()
