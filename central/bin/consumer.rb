require 'sneakers'
require 'json'
require 'influxdb'
require 'redis'

Sneakers.configure workers: 1, threads: 1, log: 'log/sneakers.log'
Sneakers.logger.level = Logger::INFO

class StateProcessor
  include Sneakers::Worker

  from_queue 'state',
             routing_key: 'measurements.#',
             exchange: 'homeauto',
             exchange_type: :topic,
             durable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.info "State update: #{message}"
    location = message['location']
    kind = message['kind']
    value = message['value']
    StateProcessor.redis.sadd 'locations', location
    StateProcessor.redis.sadd "locations:#{location}:measurements", kind
    StateProcessor.redis.set "state:#{location}:#{kind}", value
    ack!
  end

  def self.redis
    @redis ||= Redis.new
  end
end

class StatisticsProcessor
  include Sneakers::Worker

  from_queue 'statistics',
             routing_key: 'measurements.#',
             exchange: 'homeauto',
             exchange_type: :topic,
             durable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.info "Statistics: #{message}"
    data = {
      values: { value: message['value'] },
      tags: { location: message['location'] },
      timestamp: message['timestamp'],
    }
    StatisticsProcessor.influxdb.write_point message['kind'], data
    ack!
  end

  def self.influxdb
    @influxdb ||= InfluxDB::Client.new 'autohome'
  end
end
