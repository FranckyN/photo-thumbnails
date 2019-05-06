#! /usr/bin/env sh

./scripts/wait-for.sh postgres:5432 -- echo "postgres is up"
./scripts/wait-for.sh rabbitmq:5672 -- echo "rabbitmq is up"

python -u src/services/photo_processor_consumer.py &
python -u src/services/web.py
