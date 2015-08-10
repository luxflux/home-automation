require 'redis'
require 'influxdb'

module Web::Controllers::Locations
  class Show
    include Web::Action

    expose :location
    expose :measurements

    def call(params)
      @location = LocationRepository.find(params[:id])
      @states = StateRepository.all(@location.id)
      @values = ValueRepository.all(@location.id)
      @measurements = []
      @values.each do |measurement|
        query = "SELECT mean(value) FROM #{measurement.kind} WHERE time > now() - 1h GROUP BY time(1m)"
        data = influxdb.query query
        data.map! { |result| result['values'] }
        data.flatten!
        @measurements << { name: measurement.kind, current: measurement.current, data: data }
      end

      @states.each do |measurement|
        query = "SELECT mean(state) FROM #{measurement.kind} WHERE time > now() - 1h GROUP BY time(1m)"
        data = influxdb.query query
        data.map! { |result| result['values'] }
        data.flatten!
        @measurements << { name: measurement.kind, current: measurement.current, data: data }
      end
    end

    def redis
      @redis ||= Redis.new
    end

    def influxdb
      @influxdb ||= InfluxDB::Client.new 'autohome'
    end
  end
end
