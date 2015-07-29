require 'redis'

module Web::Controllers::Locations
  class Index
    include Web::Action

    expose :locations

    def call(params)
      @locations = Redis.new.smembers 'locations'
    end
  end
end
