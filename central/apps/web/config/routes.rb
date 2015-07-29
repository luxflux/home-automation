# Configure your routes here
# See: http://www.rubydoc.info/gems/lotus-router/#Usage

resources :locations

get '/', to: 'locations#index'
