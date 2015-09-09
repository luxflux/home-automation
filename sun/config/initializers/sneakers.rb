require 'sneakers'
Sneakers.configure workers: 1, threads: 1, log: Rails.root.join('log/sneakers.log')
Sneakers.logger.level = Logger::DEBUG
