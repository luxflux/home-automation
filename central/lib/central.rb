require 'lotus/model'
Dir["#{__dir__}/central/**/*.rb"].each { |file| require_relative file }

Lotus::Model.configure do
  ##
  # Database adapter
  #
  # Available options:
  #
  #  * Memory adapter
  #    adapter type: :memory, uri: 'memory://localhost/central_development'
  #
  #  * SQL adapter
  #    adapter type: :sql, uri: 'sqlite://db/central_development.sqlite3'
  #    adapter type: :sql, uri: 'postgres://localhost/central_development'
  #    adapter type: :sql, uri: 'mysql://localhost/central_development'
  #
  adapter type: :redis, uri: ENV['CENTRAL_REDIS_URL']

  ##
  # Database mapping
  #
  # Intended for specifying application wide mappings.
  #
  # You can specify mapping file to load with:
  #
  # mapping "#{__dir__}/config/mapping"
  #
  # Alternatively, you can use a block syntax like the following:
  #
  mapping do
    collection :locations do
      entity Location
      repository LocationRepository

      attribute :id, Integer
      attribute :name, String
    end

    collection :measurements do
      entity Measurement
      repository MeasurementRepository

      attribute :id, Integer
      attribute :kind, String
      attribute :current, Float
      attribute :location_id, Integer
    end
  end
end.load!

Sneakers.configure workers: 1, threads: 1, log: 'log/sneakers.log'
Sneakers.logger.level = Logger::INFO
