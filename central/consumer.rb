require 'sneakers'

class TemperatureProcessor
  include Sneakers::Worker

  from_queue '#.temperature',
             exchange: 'measurements',
             exchange_type: :topic,
             durable: true

  def work(message)
    puts message
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
    puts message
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
    puts message
    ack!
  end
end
