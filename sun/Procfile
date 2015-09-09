web: bundle exec puma -b unix://$BOXEN_SOCKET_DIR/sun -C ./config/puma.rb
state_processor: WORKERS=StateProcessor bundle exec rake sneakers:run
