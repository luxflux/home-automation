require 'rails_helper'

RSpec.describe Metric, type: :model do
  it { is_expected.to belong_to(:location) }
  it { is_expected.to validate_presence_of(:name) }
  it { is_expected.to validate_uniqueness_of(:name) }
  it { is_expected.to validate_presence_of(:location) }
end
