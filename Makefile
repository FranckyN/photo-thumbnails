export PG_USERNAME=waldo
export PG_PASSWORD=1234
export PG_DATABASE=waldo
export PG_CONNECTION_URI=postgres://$(PG_USERNAME):$(PG_PASSWORD)@postgres/$(PG_DATABASE)
export PG_CONNECTION_URI_TEST=postgres://$(PG_USERNAME):$(PG_PASSWORD)@postgres-test/$(PG_DATABASE)

export AMQP_USERNAME=rabbitmq
export AMQP_PASSWORD=1234
export AMQP_URI=amqp://$(AMQP_USERNAME):$(AMQP_PASSWORD)@rabbitmq:5672/%2f
export AMQP_URI_TEST=amqp://$(AMQP_USERNAME):$(AMQP_PASSWORD)@rabbitmq-test:5672/%2f

export STORAGE_THUMBS=/waldo-app-thumbs
export TEST_RESULTS=/test-results

start:
	docker-compose up --build

db-schema:
	docker exec -i postgres psql $(PG_CONNECTION_URI) -t < scripts/db-schema.sql

psql:
	docker exec -it postgres psql $(PG_CONNECTION_URI)
    
test:
	cd integration-tests; docker-compose up --force-recreate --build --abort-on-container-exit; docker rm postgres-test rabbitmq-test waldo-app-test test-app; docker volume rm integration-tests_psgrdata-test integration-tests_rabbitdata-test integration-tests_thumbs-folder-test
