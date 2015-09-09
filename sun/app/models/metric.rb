class Metric < ActiveRecord::Base
  belongs_to :location

  validates :name, :location, presence: true
  validates :name, uniqueness: true
end
