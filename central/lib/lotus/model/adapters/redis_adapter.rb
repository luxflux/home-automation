require 'lotus/model/adapters/abstract'
require 'lotus/model/adapters/implementation'
require 'lotus/model/adapters/redis/collection'
require 'lotus/model/adapters/redis/command'
require 'lotus/model/adapters/redis/query'

require 'redis'

module Lotus
  module Model
    module Adapters
      # Redis adapter that behaves like a SQL database.
      # Not all the features of the SQL adapter are supported.
      #
      # @see Lotus::Model::Adapters::Implementation
      #
      # @api private
      # @since 0.1.0
      class RedisAdapter < Abstract
        include Implementation

        attr_reader :connection

        # Initialize the adapter.
        #
        # @param mapper [Object] the database mapper
        # @param uri [String] the connection uri (ignored)
        #
        # @return [Lotus::Model::Adapters::RedisAdapter]
        #
        # @see Lotus::Model::Mapper
        #
        # @api private
        # @since 0.1.0
        def initialize(mapper, uri = nil)
          super

          @collections = {}
          @connection = ::Redis.new(url: uri)
        end

        # Creates a record in the database for the given entity.
        # It assigns the `id` attribute, in case of success.
        #
        # @param collection [Symbol] the target collection (it must be mapped).
        # @param entity [#id=] the entity to create
        #
        # @return [Object] the entity
        #
        # @api private
        # @since 0.1.0
        def create(collection, entity)
          command(collection).create(entity)
        end


        # Updates a record in the database corresponding to the given entity.
        #
        # @param collection [Symbol] the target collection (it must be mapped).
        # @param entity [#id] the entity to update
        #
        # @return [Object] the entity
        #
        # @api private
        # @since 0.1.0
        def update(collection, entity)
          command(collection).update(entity)
        end

        # Fabricates a query
        #
        # @param collection [Symbol] the target collection (it must be mapped).
        # @param blk [Proc] a block of code to be executed in the context of
        #   the query.
        #
        # @return [Lotus::Model::Adapters::Redis::Query]
        #
        # @see Lotus::Model::Adapters::Redis::Query
        #
        # @api private
        # @since 0.1.0
        def query(collection, _context = nil, &blk)
          Redis::Query.new(_collection(collection), _mapped_collection(collection), &blk)
        end

        # Returns a collection from the given name.
        #
        # @param name [Symbol] a name of the collection (it must be mapped).
        #
        # @return [Lotus::Model::Adapters::Redis::Collection]
        #
        # @see Lotus::Model::Adapters::Redis::Collection
        #
        # @api private
        # @since 0.1.0
        def _collection(name)
          @collections[name] ||= Redis::Collection.new(connection, name, _mapped_collection(name))
        end

        # Fabricates a command for the given query.
        #
        # @param collection [Symbol] the collection name (it must be mapped)
        #
        # @return [Lotus::Model::Adapters::Redis::Command]
        #
        # @see Lotus::Model::Adapters::Redis::Command
        #
        # @api private
        # @since 0.1.0
        def command(collection)
          Redis::Command.new(_collection(collection), _mapped_collection(collection))
        end

        def find(collection, id)
          identity = _identity(collection)
          query(collection).find(_id(collection, identity, id))
        end
      end
    end
  end
end
