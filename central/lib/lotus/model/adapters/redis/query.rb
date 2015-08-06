require 'lotus/model/adapters/memory/query'

module Lotus
  module Model
    module Adapters
      module Redis
        class Query < Lotus::Model::Adapters::Memory::Query
          include Enumerable
          extend  Forwardable

          def_delegators :all, :each, :to_s, :empty?

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
            @conditions = []
            @modifiers = []
            instance_eval(&blk) if block_given?
          end

          # Resolves the query by fetching records from the database and
          # translating them into entities.
          #
          # @return [Array] a collection of entities
          #
          # @since 0.1.0
          def all
            result = typecast_set(symbolize_keys_in_set(@dataset.all))

            if conditions.any?
              prev_result = nil
              conditions.each do |(type, condition)|
                case type
                when :where
                  prev_result = result
                  result = prev_result.instance_exec(&condition)
                when :or
                  result |= prev_result.instance_exec(&condition)
                end
              end
            end

            modifiers.map do |modifier|
              result.instance_exec(&modifier)
            end

            Lotus::Utils::Kernel.Array(@collection.deserialize(result))
          end

          def find(id)
            @collection.deserialize([symbolize_keys(@dataset.find(id))]).first
          end

          private

          def symbolize_keys_in_set(set)
            set.map { |record| symbolize_keys(record) }
          end

          def symbolize_keys(record)
            record.each_with_object({}) { |(k, v), h| h[k.to_sym] = v }
          end

          def typecast_set(records)
            @collection.deserialize(records).map { |record| @collection.serialize(record) }
          end
        end
      end
    end
  end
end
