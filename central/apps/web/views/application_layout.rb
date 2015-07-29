require 'lotus/assets'
require 'lotus/assets/helpers'

module Web
  module Views
    class ApplicationLayout
      include Web::Layout
      include Lotus::Assets::Helpers
    end
  end
end
