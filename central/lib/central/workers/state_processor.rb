require 'sneakers'
require 'json'

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
    new_value = message['value']
    new_state = message['state']

    Sneakers.logger.info "Ensure location #{location_name} exists"
    location = LocationRepository.find_by_name(location_name)
    location ||= Location.new(name: location_name)
    LocationRepository.persist location

    if new_state
      Sneakers.logger.info "Update state #{location_name}/#{kind} to #{new_state}"
      state = StateRepository.find_by_kind(location.id, kind)
      state ||= State.new(kind: kind, location_id: location.id)
      state.current = new_state
      StateRepository.persist state
    end

    if new_value
      Sneakers.logger.info "Update value #{location_name}/#{kind} to #{new_value}"
      value = ValueRepository.find_by_kind(location.id, kind)
      value ||= Value.new(kind: kind, location_id: location.id)
      value.current = new_value
      ValueRepository.persist value
    end
    ack!
  end
end
