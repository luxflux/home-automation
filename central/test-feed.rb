require 'sneakers'
require 'sneakers/publisher'
require 'json'

Sneakers.configure logger: ::Logger.new(STDOUT)

Sneakers.logger.level = ::Logger::INFO

publisher = Sneakers::Publisher.new exchange: 'measurements', exchange_type: :topic

loop do
  [
    { location: 'test', kind: 'movement', value: [true, false].sample, timestamp: Time.now.to_i },
    { location: 'test', kind: 'humidity', value: Kernel.rand(100), timestamp: Time.now.to_i },
    { location: 'test', kind: 'temperature', value: Kernel.rand(20..33), timestamp: Time.now.to_i },
  ].each do |message|
    publisher.publish(JSON.dump(message), to_queue: "#{message[:location]}.#{message[:kind]}")
  end

  # sleep Kernel.rand
end
