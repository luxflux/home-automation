# config valid only for current version of Capistrano
lock '3.4.0'

set :application, 'central'
set :repo_url, 'git@github.com:luxflux/home-automation'
set :repo_tree, 'central'

# Default deploy_to directory is /var/www/my_app_name
set :deploy_to, '/srv/autohome'

# Default value for linked_dirs is []
set :linked_dirs, fetch(:linked_dirs, []).push('log', 'vendor/bundle', 'tmp/sockets')

set :rbenv_type, :system
set :rbenv_ruby, '2.2.2'

set :passenger_restart_with_touch, true
