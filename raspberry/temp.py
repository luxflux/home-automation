#!/usr/bin/env python

try:
    import RPi.GPIO as GPIO
    import time
    import Adafruit_DHT
    import spidev

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)

    light_sensor = 0 # analog
    uv_sensor = 1 # analog
    dummy_sensor = 2 # analog
    movement_sensor = 4
    temperature_sensor_pin = 3
    temperature_sensor_type = Adafruit_DHT.DHT22

    GPIO.setup(movement_sensor, GPIO.IN)

    spi = spidev.SpiDev()
    spi.open(0,0)

    # Function to read SPI data from MCP3008 chip
    # Channel must be an integer 0-7
    def ReadChannel(channel):
        adc = spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data

    while True:
        light_reading = ReadChannel(light_sensor)
        uv_reading = ReadChannel(uv_sensor)
        dummy_reading = ReadChannel(dummy_sensor)

        movement = GPIO.input(movement_sensor)
        humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor_type, temperature_sensor_pin)

        print "==================="
        print "LIGHT: %d" % light_reading
        print "UV: %d" % uv_reading
        print "DUMMY: %d" % dummy_reading
        print "MOVEMENT: %d" % movement
        print "HUMIDITY: %f" % humidity
        print "TEMPERATURE: %f" % temperature

        time.sleep(1)

finally: GPIO.cleanup()
