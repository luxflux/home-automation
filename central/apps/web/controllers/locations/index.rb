require 'redis'

module Web::Controllers::Locations
  class Index
    include Web::Action

    expose :locations

    def call(params)
      # LocationRepository.create(Location.new(name: 'test'))
      @locations = LocationRepository.all
    end
  end
end
