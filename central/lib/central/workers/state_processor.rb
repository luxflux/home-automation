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
    value = message['value']

    Sneakers.logger.info "Ensure location #{location_name} exists"
    location = LocationRepository.find_by_name(location_name)
    location ||= Location.new(name: location_name)
    LocationRepository.persist location

    Sneakers.logger.info "Update current measurement of #{location_name}/#{kind}"
    measurement = MeasurementRepository.find_by_kind(location.id, kind)
    measurement ||= Measurement.new(kind: kind, location_id: location.id)
    measurement.current = value
    MeasurementRepository.persist measurement
    ack!
  end
end
