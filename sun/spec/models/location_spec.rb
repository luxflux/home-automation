require 'rails_helper'

RSpec.describe Location, type: :model do
  it { is_expected.to have_many(:metrics) }
  it { is_expected.to validate_presence_of(:name) }
  it { is_expected.to validate_uniqueness_of(:name) }
end
