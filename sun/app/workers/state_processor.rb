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
    location_name = message['location']
    kind = message['kind']
    value = message['value']

    Sneakers.logger.info "Ensure location #{location_name} exists"
    location = Location.where(name: location_name).first_or_create!

    Sneakers.logger.info "Update current value of #{location_name}/#{kind} to #{value}"
    metric = location.metrics.where(name: kind).first_or_create!
    metric.update current: value

    ack!
  end
end
