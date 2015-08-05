require 'rubygems'
require 'bundler/setup'
require 'lotus/setup'

$: << File.expand_path('../../lib', __FILE__)
require 'central'
require_relative '../apps/web/application'

Lotus::Container.configure do
  mount Web::Application, at: '/'
end
