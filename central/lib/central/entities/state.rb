require 'lotus/model'

class State
  include Lotus::Entity

  attributes :kind, :current, :location_id
end
