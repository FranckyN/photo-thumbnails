FROM python:3.7.2-alpine3.9

RUN mkdir /test_app
WORKDIR /test_app

RUN apk add --no-cache build-base jpeg-dev zlib-dev postgresql-dev

RUN pip install pipenv

COPY Pipfile Pipfile
RUN pipenv lock

RUN pipenv install --deploy --system

COPY db-schema.sql db-schema-test-1.sql

COPY conftest.py conftest.py
COPY test_app.py test_app.py

CMD ["pytest", "-v", "-s", "--junitxml=/results/report.xml"]
