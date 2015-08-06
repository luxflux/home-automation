require 'lotus/model'

class LocationRepository
  include Lotus::Repository

  def self.all
    query do
      order(:name)
    end
  end

  def self.find_by_name(name)
    query do
      where(name: name)
    end.limit(1).first
  end
end
