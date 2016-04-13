#!/usr/bin/env python

import os
import time
import RPi.GPIO
import Adafruit_DHT
import spidev
import pika
import json
import signal
import sys
import logging
import numbers


config = [
        # { 'type': 'analog', 'port': 1, 'module': 'light' },
        { 'type': 'analog', 'port': 5, 'module': 'uv' },
        { 'type': 'digital', 'port': 1, 'module': 'movement' },
        # { 'type': 'digital', 'port': 2, 'module': 'environment' },
        ]


def format_log(hash):
  outarr = []
  for k,v in hash.items():
    if v is None:
      outarr.append("%s=" % k)
      continue

    if isinstance(v, bool):
        v = "true" if v else "false"

    elif isinstance(v, numbers.Number ):
        pass

    else:
      if isinstance(v, (dict, object)):
        v = str(v)

      v = '"%s"' % v.replace('"', '\\' + '"')

    outarr.append("%s=%s" % (k, v))

  return " ".join(outarr)

def info(tag, hash):
    hash['tag'] = tag
    hash['level'] = 'info'
    logging.info(format_log(hash))

def debug(tag, hash):
    hash['tag'] = tag
    hash['level'] = 'debug'
    logging.debug(format_log(hash))

class MissingConfigVariable(Exception):
    def __init__(self, name, element = None):
        self.element = None
        self.name = name

    def __str__(self):
        if element:
            return repr("Missing ENV Variable %s in %s" % self.name,
                    self.element)
        else:
            return repr("Missing ENV Variable %s" % self.name)


class SPI(object):
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)

    def read(self, channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data


class GPIO(object):
    BCM_PORT_MAPPING = {
            1: 14,
            2: 15,
            3: 18,
            4: 17,
            5: 27,
            }

    def __init__(self):
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(True)

        for port, bcm_port in self.BCM_PORT_MAPPING.iteritems():
            debug('setup_port', { 'port': port, 'bcm_port': bcm_port })
            RPi.GPIO.setup(bcm_port, RPi.GPIO.IN)

    def read(self, port):
        bcm_port = self.BCM_PORT_MAPPING.get(port)
        debug('reading_bcm', { 'bcm_port': bcm_port })
        return RPi.GPIO.input(bcm_port)


class AnalogPort(object):
    def __init__(self, spi, gpio, port):
        self.port = port
        self.spi = spi

    def read(self):
        return self.spi.read(self.port - 1)


class AnalogUV(AnalogPort):
    ""


class DigitalPort(object):
    def __init__(self, spi, gpio, port):
        self.port = port
        self.gpio = gpio

    def read(self):
        debug('reading_digital_port', { 'port': self.port })
        value = self.gpio.read(self.port)
        debug('reading_digital_port_completed',
                { 'port': self.port, 'value': value })
        return value


class DigitalMovement(DigitalPort):
    def read(self):
        return super(DigitalMovement, self).read() == 1


class AMQP:
    def __init__(self, user, password, host, exchange, location, port = 5672):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.exchange = exchange
        self.location = location
        self.channel = self.connect()

    def publish(self, type, port, value):
        message = {
                'location': self.location,
                'port': port,
                'type': type,
                'value': value,
                'timestamp': int(time.time())}

        debug('amqp_publish', message)
        self.channel.basic_publish(
                exchange=self.exchange,
                routing_key='measurements.%s'.format(self.location),
                body=json.dumps(message)
        )

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(self.host, self.port, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        return connection.channel()


class Moon:
    SWITCHER = {
            'analog': {
                # light: AnalogLight,
                'uv': AnalogUV,
                },
            'digital': {
                'movement': DigitalMovement,
                #     environment: DigitalEnvironment,
                }
            }

    def __init__(self, config, amqp_config, location):
        self.config = config
        self.amqp_config = amqp_config
        self.validate_config
        self.validate_amqp_config
        self.spi = SPI()
        self.gpio = GPIO()
        self.amqp = AMQP(
                amqp_config['user'],
                amqp_config['password'],
                amqp_config['host'],
                amqp_config['exchange'],
                location)

    def validate_config():
        for config in self.config:
            for variable in ['type', 'port', 'module']:
                if not config.has_key(variable):
                    raise MissingConfigVariable(variable, config)

    def validate_amqp_config():
        for variable in ['user', 'password', 'host', 'exchange']:
            if not amqp_config.has_key(variable):
                raise MissingConfigVariable(variable)

    def run(self):
        for port in self.config:
            debug('start_handling', port)
            klass = self.SWITCHER.get(port['type']).get(port['module'])
            reader = klass(self.spi, self.gpio, port['port'])

            value = reader.read()
            info('reading_complete', {
                'value': value,
                'port_type': port['type'],
                'port': port['port']
                })
            self.amqp.publish(port['type'], port['port'], value)


def main():
    amqp_config = {
            'user': os.environ['AMQP_USER'],
            'password': os.environ['AMQP_PASSWORD'],
            'host': os.environ['AMQP_HOST'],
            'exchange': os.environ['AMQP_EXCHANGE'],
            }
    moon = Moon(config, amqp_config, os.environ['MOON_LOCATION'])

    while True:
        moon.run()
        time.sleep(1)

def signal_handler(signal, frame):
    info('got_ctrlc', {})
    RPi.GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
numeric_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper(), None)
logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
main()
