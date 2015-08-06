require 'redis'

module Web::Controllers::Locations
  class Index
    include Web::Action

    expose :locations

    def call(params)
      @locations = LocationRepository.all
    end
  end
end
