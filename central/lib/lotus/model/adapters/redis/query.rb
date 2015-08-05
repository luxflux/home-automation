module Lotus
  module Model
    module Adapters
      module Redis
        class Query
          # Initialize a query
          #
          # @param dataset [Lotus::Model::Adapters::Redis::Collection]
          # @param collection [Lotus::Model::Mapping::Collection]
          # @param blk [Proc] an optional block that gets yielded in the
          #   context of the current query
          #
          # @since 0.1.0
          # @api private
          def initialize(dataset, collection, &blk)
            @dataset = dataset
            @collection = collection
            instance_eval(&blk) if block_given?
          end

          # Resolves the query by fetching records from the database and
          # translating them into entities.
          #
          # @return [Array] a collection of entities
          #
          # @since 0.1.0
          def all
            @collection.deserialize(run)
          end

          private

          # Apply all the conditions and returns a filtered collection.
          #
          # This operation is idempotent, but the records are actually fetched
          # from the memory store.
          #
          # @return [Array]
          #
          # @api private
          # @since 0.1.0
          def run
            @dataset.all.map { |record| record.each_with_object({}) { |(k,v), h| h[k.to_sym] = v } }
          end
        end
      end
    end
  end
end
