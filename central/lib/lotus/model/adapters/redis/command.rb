module Lotus
  module Model
    module Adapters
      module Redis
        # Execute a command for the given collection.
        #
        # @see Lotus::Model::Adapters::Redis::Collection
        # @see Lotus::Model::Mapping::Collection
        #
        # @api private
        # @since 0.1.0
        class Command
          # Initialize a command
          #
          # @param dataset [Lotus::Model::Adapters::Redis::Collection]
          # @param collection [Lotus::Model::Mapping::Collection]
          #
          # @api private
          # @since 0.1.0
          def initialize(dataset, collection)
            @dataset    = dataset
            @collection = collection
          end

          # Creates a record for the given entity.
          #
          # @param entity [Object] the entity to persist
          #
          # @see Lotus::Model::Adapters::Redis::Collection#insert
          #
          # @return the primary key of the just created record.
          #
          # @api private
          # @since 0.1.0
          def create(entity)
            @dataset.create(entity)
          end
        end
      end
    end
  end
end
