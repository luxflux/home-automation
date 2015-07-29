require 'sneakers'
require 'json'
require 'influxdb'

Sneakers.configure workers: 1, threads: 1, log: 'log/sneakers.log'
Sneakers.logger.level = Logger::INFO

class TemperatureProcessor
  include Sneakers::Worker

  from_queue '#.temperature',
             exchange: 'measurements',
             exchange_type: :topic,
             durable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.debug "Temperature: #{message}"
    StatisticsProcessor.enqueue JSON.dump(message)
    ack!
  end
end

class HumidityProcessor
  include Sneakers::Worker

  from_queue '#.humidity',
             exchange: 'measurements',
             exchange_type: :topic,
             durable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.debug "Humidity: #{message}"
    StatisticsProcessor.enqueue JSON.dump(message)
    ack!
  end
end

class MovementProcessor
  include Sneakers::Worker

  from_queue '#.movement',
             exchange: 'measurements',
             exchange_type: :topic,
             durable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.debug "Movement: #{message}"
    StatisticsProcessor.enqueue JSON.dump(message)
    ack!
  end
end

class StatisticsProcessor
  include Sneakers::Worker

  from_queue 'statistics',
             idurable: true

  def work(message)
    message = JSON.parse(message)
    Sneakers.logger.debug "Statistics: #{message}"
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
