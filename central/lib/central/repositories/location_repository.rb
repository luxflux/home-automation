require 'lotus/model'

class LocationRepository
  include Lotus::Repository

  def self.all
    query do
      order(:name)
    end
  end
end
