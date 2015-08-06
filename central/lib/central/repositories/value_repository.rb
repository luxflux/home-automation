require 'lotus/model'

class ValueRepository
  include Lotus::Repository

  def self.all(location_id)
    query do
      where(location_id: location_id)
      order(:kind)
    end
  end

  def self.find_by_kind(location_id, kind)
    query do
      where(location_id: location_id)
      where(kind: kind)
    end.limit(1).first
  end
end
