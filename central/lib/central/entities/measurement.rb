require 'lotus/model'

class Measurement
  include Lotus::Entity

  attributes :kind, :current, :location_id
end
