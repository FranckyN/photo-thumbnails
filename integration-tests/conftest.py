import pytest
import requests as rq
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import os


g_ms = "https://s3.amazonaws.com/waldo-thumbs-dev/large/366ad885-aafd-48a4-8ff5-c38a1bbc84c8.jpg"
g_uuid = 'd35bf2dc-f666-49e9-8d26-5a160573af5c'


@pytest.fixture
def ms_uuids():
    def db_s_uuid():
        return g_uuid
    return db_s_uuid


@pytest.fixture
def all_uuids():
    photos_uuids = get_photos_uuid()

    def s_photo_uuid():
        return photos_uuids
    return s_photo_uuid


def app_url():
    return "http://waldo-app-test:3000"


@pytest.fixture
def get_base_url():
    return app_url()


def get_url(base_url, token):
    return "{}/{}".format(base_url, token)


@pytest.fixture
def get_url_process(get_base_url):
    return get_url(get_base_url, 'photos/process')


@pytest.fixture
def get_url_pending(get_base_url):
    return get_url(get_base_url, 'photos/pending')


@pytest.fixture(scope="session", autouse=True)
def session_beginning():
    wait_for_service()
    generate_data()
    yield
    clean_data()


def wait_for_service():
    nb_retries = 0
    while nb_retries < 30:
        try:
            print("waiting...")
            response = rq.get(app_url())
            if response.status_code == 200:
                print("connection success")
                return True
        except:
            pass
        nb_retries += 1
        time.sleep(5)
    print("service not ready")


def generate_data():
    with open('db-schema-test-1.sql', 'r') as file:
        statements = " ".join(file.readlines())
        connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(statements)
        finally:
            connection.close()


def clean_data():
    connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(("DROP TABLE IF EXISTS photo_thumbnails; "
                                "DROP TABLE IF EXISTS photos; "
                                "DROP TYPE IF EXISTS photo_status;"))
    finally:
        connection.close()


def get_photos_uuid():
    connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT uuid FROM photos")
                photos_uuids = cursor.fetchall()
                return [x['uuid'] for x in photos_uuids]
    finally:
        connection.close()


@pytest.fixture
def db_update_status():
    def update_status(status, uuid):
        connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("UPDATE photos SET status=%s WHERE uuid=%s", (status, uuid))
        finally:
            connection.close()
    return update_status


@pytest.fixture
def db_thumbnail():
    def get_thumbnail_data(uuid):
        connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT url,width,height FROM photo_thumbnails WHERE photo_uuid=%s",
(uuid,))
                    data = cursor.fetchone()
                    return {"url": data["url"], "width": data["width"], "height": data["height"]}
        finally:
            connection.close()
    return get_thumbnail_data


@pytest.fixture
def db_photo_status():
    def get_photos_status(uuid):
        connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT status FROM photos WHERE uuid=%s",
                                   (uuid,))
                    photos_status = cursor.fetchone()
                    if cursor.rowcount > 0:
                        return photos_status["status"]
        finally:
            connection.close()
    return get_photos_status


@pytest.fixture
def db_insert_missing_image():
    def insert_missing_image():
        connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("INSERT INTO photos (uuid, url) VALUES (%s,%s)",
                                   (g_uuid, g_ms))
        finally:
            connection.close()
    return insert_missing_image


@pytest.fixture
def db_delete_missing_image():
    def delete_missing_image():
        connection = psycopg2.connect(os.environ['PG_CONNECTION_URI'])
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("DELETE FROM photos WHERE url=%s", (g_ms,))
        finally:
            connection.close()
    return delete_missing_image
