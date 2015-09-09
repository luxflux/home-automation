class Location < ActiveRecord::Base
  has_many :metrics

  validates :name, presence: true
  validates :name, uniqueness: true
end
