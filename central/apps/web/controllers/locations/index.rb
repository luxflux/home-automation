require 'redis'

module Web::Controllers::Locations
  class Index
    include Web::Action

    expose :locations

    def call(params)
      # LocationRepository.create(Location.new(name: %w(test asd jjs 44s).sample))
      @locations = LocationRepository.all
    end
  end
end
