require 'sneakers'
require 'json'
require 'influxdb'
require 'redis'

Sneakers.configure workers: 1, threads: 1, log: 'log/sneakers.log'
Sneakers.logger.level = Logger::INFO

class StatisticsProcessor
  BOOL_MAPPING = { true => 1, false => 0 }

  include Sneakers::Worker

  from_queue 'statistics',
             routing_key: 'measurements.#',
             exchange: 'homeauto',
             exchange_type: :topic,
             durable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.info "Statistics: #{message}"
    values = {}
    values[:value] = message['value'] if message['value']
    values[:state] = BOOL_MAPPING[message['state']] if !message['state'].nil?
    data = {
      values: values,
      tags: { location: message['location'] },
      timestamp: message['timestamp'],
    }
    Sneakers.logger.info "Writing #{data}"
    StatisticsProcessor.influxdb.write_point message['kind'], data
    ack!
  end

  def self.influxdb
    @influxdb ||= InfluxDB::Client.new 'autohome'
  end
end
