require 'redis'
require 'influxdb'

module Web::Controllers::Locations
  class Show
    include Web::Action

    expose :location
    expose :measurements

    def call(params)
      @location = LocationRepository.find(params[:id])
      @measurements = MeasurementRepository.all(@location.id)
      # @states = measurements.map do |measurement|
      #   # data = influxdb.query "SELECT mean(value) FROM #{measurement} WHERE time > now() - 1h GROUP BY time(1m)"
      #   # data.map! { |result| result['values'] }
      #   # data.flatten!
      #   { name: measurement, current: measurement.current, data: data }
      # end
    end

    def redis
      @redis ||= Redis.new
    end

    def influxdb
      @influxdb ||= InfluxDB::Client.new 'autohome'
    end
  end
end
