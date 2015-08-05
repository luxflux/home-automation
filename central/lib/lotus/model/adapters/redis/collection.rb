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
            records
          end

          # @attr_reader records [Hash] a set of records
          #
          # @since 0.1.0
          # @api private
          def records
            ids = @connection.smembers name
            ids.map { |id| @connection.hgetall id }
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
            serialized_entity = _serialize(entity)

            id = @connection.incr "#{name}:id"
            serialized_entity[_identity] = id
            identifier = "#{name}:#{id}"
            @connection.mapped_hmset identifier, serialized_entity
            @connection.sadd name, identifier

            _deserialize(serialized_entity)
          end

          private

          # Serialize the given entity before to persist in the database.
          #
          # @return [Hash] the serialized entity
          #
          # @api private
          # @since 0.1.0
          def _serialize(entity)
            @mapped_collection.serialize(entity)
          end

          # Deserialize the given entity after it was persisted in the database.
          #
          # @return [Lotus::Entity] the deserialized entity
          #
          # @api private
          # @since 0.2.2
          def _deserialize(entity)
            @mapped_collection.deserialize([entity]).first
          end

          # Name of the identity column in database
          #
          # @return [Symbol] the identity name
          #
          # @api private
          # @since 0.2.2
          def _identity
            @mapped_collection.identity
          end
        end
      end
    end
  end
end
