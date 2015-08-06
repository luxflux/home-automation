require 'lotus/model'

class Value
  include Lotus::Entity

  attributes :kind, :current, :location_id
end
