"""
    apps_db_manager
    ~~~~~~~~~~~~~
    Manages access to database and implements all necessary queries.
    copyright: ©2019 by Franck Nassé
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging
import apps_logger as apl


def Logger():
    return logging.getLogger(__name__)

apl.configure_logger(Logger())


class db_manager:
    """
    Class that manages the connections to the database using a pool.
    """
    __pool = ThreadedConnectionPool(2, 10,
                                    os.environ['PG_CONNECTION_URI'])

    def __init__(self):
        pass

    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        gets a connection from the pool
        """
        try:
            connection = cls.__pool.getconn()
            yield connection
        finally:
            try:
                if connection:
                    cls.__pool.putconn(connection)
            except:
                pass

    @classmethod
    @contextmanager
    def get_cursor(cls, commit_too=False):
        """
        get a cursor and closes it afterwards
        """
        with cls.get_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                if commit_too:
                    connection.commit()
            finally:
                cursor.close()

    @classmethod
    def get_photos_by_status(cls, status: str):
        """
        Returns all photo records with the same status
        (e.g. 'pending','completed', etc.)
        """
        try:
            with cls.get_cursor() as cursor:
                the_query = "SELECT * from photos WHERE status = %s"
                cursor.execute(the_query, (status,))
                photo_records = cursor.fetchall()
                return photo_records
        except Exception as error:
            Logger().error(str(error))
            raise

    @classmethod
    def get_photo_status(cls, current_uuid: str):
        """
        Returns status of a photo given its uuid.
        """
        try:
            with cls.get_cursor() as cursor:
                the_query = "SELECT status from photos WHERE uuid=%s"
                cursor.execute(the_query, (current_uuid,))
                photo_records = cursor.fetchone()
                if cursor.rowcount > 0:
                    return photo_records["status"]
        except Exception as error:
                Logger().error(str(error))
        return ''

    @classmethod
    def update_photo_status(cls, current_uuid: str, status_value: str):
        """
        Updates status of a photo given an uuid.
        """
        try:
            with cls.get_cursor(True) as cursor:
                the_query = "UPDATE photos set status=%s WHERE uuid=%s"
                cursor.execute(the_query, (status_value, current_uuid))
        except Exception as error:
            Logger().error(str(error))
            raise

    @classmethod
    def get_photos_column(cls, current_uuid: str, column: str) -> str:
        """
        Return the value of a specific column of photos given an uuid.
        """
        try:
            with cls.get_cursor() as cursor:
                the_query = "SELECT {} FROM photos WHERE uuid=%s". \
                             format(column)
                cursor.execute(the_query, (current_uuid,))
                photo_column = cursor.fetchone()
                if cursor.rowcount > 0:
                    return photo_column[column]
        except Exception as error:
                Logger().error(str(error))
        return ''

    @classmethod
    def insert_new_thumbnail(cls, photo_details):
        """
        Given the details of photo, insert a new record in photo_thumbnails.
        """
        try:
            with cls.get_cursor(True) as cursor:
                the_query = """INSERT INTO photo_thumbnails (
                photo_uuid, width, height, url) VALUES (%s, %s, %s, %s)"""
                cursor.execute(the_query, (photo_details["uuid"],
                                           photo_details["width"],
                                           photo_details["height"],
                                           photo_details["url"]))
        except Exception as error:
            Logger().error(str(error))
            raise
