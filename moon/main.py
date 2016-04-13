#!/usr/bin/env python

from contextlib import closing
from kombu.mixins import ConsumerMixin
import Adafruit_DHT
import RPi.GPIO
import json
import kombu
import logging
import numbers
import os
import signal
import spidev
import sys
import threading
import time

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

def warn(tag, hash):
    hash['tag'] = tag
    hash['level'] = 'warn'
    logging.debug(format_log(hash))

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
    BCM_READ_PORT_MAPPING = {
            1: 14,
            2: 15,
            3: 18,
            4: 17,
            5: 27,
            }

    BCM_WRITE_PORT_MAPPING = {
            1: 4,
            2: 3,
            3: 2,
            4: 16,
            }

    def __init__(self):
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(True)

        for port, bcm_port in self.BCM_READ_PORT_MAPPING.iteritems():
            info('setup_port', { 'port': port,
                'bcm_port': bcm_port,
                'used_for': 'read'
                })
            RPi.GPIO.setup(bcm_port, RPi.GPIO.IN)

        for port, bcm_port in self.BCM_WRITE_PORT_MAPPING.iteritems():
            info('setup_port', { 'port': port,
                'bcm_port': bcm_port,
                'used_for': 'write'
                })
            RPi.GPIO.setup(bcm_port, RPi.GPIO.OUT)

    def read(self, port):
        bcm_port = self.BCM_READ_PORT_MAPPING.get(port)
        debug('reading_bcm', { 'bcm_port': bcm_port })
        return RPi.GPIO.input(bcm_port)

    def off(self, port):
        bcm_port = self.BCM_WRITE_PORT_MAPPING.get(port)
        debug('set_off', { 'bcm_port': bcm_port })
        RPi.GPIO.output(bcm_port, 0)

    def on(self, port):
        bcm_port = self.BCM_WRITE_PORT_MAPPING.get(port)
        debug('set_on', { 'bcm_port': bcm_port })
        RPi.GPIO.output(bcm_port, 1)


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


class AMQPPublisher:
    def __init__(self, connection, location, serializer='json', compression=None):
        self.location = location
        exchange_opts = { 'type': 'topic' }
        self.queue = connection.SimpleQueue('homeauto', exchange_opts=exchange_opts)
        self.serializer = serializer
        self.compression = compression

    def publish(self, type, port, value):
        message = {'location': self.location,
                        'port': port,
                        'type': type,
                        'value': value,
                        'timestamp': int(time.time())}
        debug('amqp_publish', message)
        self.queue.put(message,
                        serializer=self.serializer,
                        compression=self.compression,
                        routing_key='measurements.{:s}'.format(self.location))

    def close(self):
        self.queue.close()

class AMQPConsumer(ConsumerMixin):
    def __init__(self, connection, location, callback):
        self.connection = connection
        self.location = location
        self.callback = callback

    def get_consumers(self, Consumer, channel):
        routing_key = 'commands.{:s}.#'.format(self.location)
        exchange = kombu.Exchange('homeauto', type='topic')
        queues = [kombu.Queue('{:s}.commands'.format(self.location),
            exchange=exchange, routing_key=routing_key)]
        return [
            Consumer(queues, callbacks=[self.on_message], accept=['json']),
        ]

    def on_message(self, body, message):
        debug('received_command', body)
        self.callback(body)
        message.ack()

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
        self.location = location

        self.amqp_url = 'amqp://{:s}:{:s}@{:s}//'.format(
                amqp_config['user'], amqp_config['password'], amqp_config['host'])

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
        self.stop_event = threading.Event()
        threads = []
        consumer_thread = threading.Thread(target=self.run_consumer)
        publisher_thread = threading.Thread(target=self.run_publisher,
                args=(2, self.stop_event))
        threads.append(consumer_thread)
        threads.append(publisher_thread)
        consumer_thread.start()
        publisher_thread.start()

        while True:
            for thread in threads:
                if thread is not None and thread.isAlive():
                    thread.join(1)

    def stop(self):
        self.stop_event.set()
        self.consumer.should_stop = True

    def run_consumer(self):
        with kombu.Connection(self.amqp_url) as conn:
            self.consumer = AMQPConsumer(conn, self.location, RelayController(GPIO()).handle)
            self.consumer.run()

    def run_publisher(self, arg1, stop_event):
        with kombu.Connection(self.amqp_url) as conn:
            with closing(AMQPPublisher(conn, self.location)) as amqp:
                while not stop_event.is_set():
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
                        amqp.publish(port['type'], port['port'], value)
                    stop_event.wait(1)



class RelayController:
    ACTION = {
            'off': lambda(self, relay): self.off(relay),
            'on': lambda(self, relay): self.on(relay),
            }

    def __init__(self, gpio):
        self.gpio = gpio

    def handle(self, message):
        debug('got_message', message)
        if message['action'] == 'on':
            self.on(message['relay'])

        elif message['action'] == 'off':
            self.off(message['relay'])

        else:
            warn('action_unknown', { 'action': message['action'] })


    def off(self, relay):
        info('set_off', { 'relay': relay })
        self.gpio.off(relay)

    def on(self, relay):
        info('set_on', { 'relay': relay })
        self.gpio.on(relay)

def signal_handler(signal, frame):
    info('got_ctrlc', {})
    RPi.GPIO.cleanup()
    moon.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

numeric_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper(), None)
logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')

amqp_config = {
        'user': os.environ['AMQP_USER'],
        'password': os.environ['AMQP_PASSWORD'],
        'host': os.environ['AMQP_HOST'],
        'exchange': os.environ['AMQP_EXCHANGE'],
        }
moon = Moon(config, amqp_config, os.environ['MOON_LOCATION'])
moon.run()
