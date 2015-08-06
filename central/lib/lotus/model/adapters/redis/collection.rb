module Lotus
  module Model
    module Adapters
      module Redis
        class Collection
          # @attr_reader name [Symbol] the name of the collection (eg. `:users`)
          #
          # @since 0.1.0
          # @api private
          attr_reader :name

          def initialize(connection, name, mapped_collection)
            @connection = connection
            @name = name
            @mapped_collection = mapped_collection
          end

          # Returns all the raw records
          #
          # @return [Array<Hash>]
          #
          # @api private
          # @since 0.1.0
          def all
            ids = @connection.smembers name
            ids.map { |id| @connection.hgetall "#{name}:#{id}" }
          end

          # Creates a record for the given entity and assigns an id.
          #
          # @param entity [Object] the entity to persist
          #
          # @see Lotus::Model::Adapters::Redis::Command#create
          #
          # @return the primary key of the created record
          #
          # @api private
          # @since 0.1.0
          def create(entity)
            id = @connection.incr "#{name}:id"
            entity[_identity] = id
            identifier = "#{name}:#{id}"
            @connection.mapped_hmset identifier, entity
            @connection.sadd name, id

            entity
          end

          def find(id)
            @connection.hgetall("#{name}:#{id}")
          end
        end
      end
    end
  end
end
