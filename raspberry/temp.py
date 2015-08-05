#!/usr/bin/env python

try:
    import RPi.GPIO as GPIO
    import time
    import Adafruit_DHT

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)

    light_sensor = 0 # analog
    uv_sensor = 1 # analog
    dummy_sensor = 4 # analog
    movement_sensor = 4
    temperature_sensor_pin = 3
    temperature_sensor_type = Adafruit_DHT.DHT22

    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
            return -1

        GPIO.output(cspin, True)
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit

        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
            if (commandout & 0x80):
                GPIO.output(mosipin, True)
            else:
                GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

    GPIO.setup(movement_sensor, GPIO.IN)

    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    while True:
        # light_reading = readadc(light_sensor, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # uv_reading = readadc(uv_sensor, SPICLK, SPIMOSI, SPIMISO, SPICS)
        dummy_reading = readadc(dummy_sensor, SPICLK, SPIMOSI, SPIMISO, SPICS)

        # movement = GPIO.input(movement_sensor)
        # humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor_type, temperature_sensor_pin)

        print "==================="
        # print "LIGHT: %d" % light_reading
        # print "UV: %d" % uv_reading
        print "DUMMY: %d" % dummy_reading
        # print "MOVEMENT: %d" % movement
        # print "HUMIDITY: %f" % humidity
        # print "TEMPERATURE: %f" % temperature

        time.sleep(1)

finally: GPIO.cleanup()
