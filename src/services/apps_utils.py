"""
    apps_utils
    ~~~~~~~~~~~~~
    Implements various utility functions.
    copyright: ©2019 by Franck Nassé
"""
import os
import uuid


def remove_file(file_path):
    """ Deletes a file, only if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def is_string_uuid(candidate_uuid):
    """ If the string input is not a valid uuid, the function return False.
    """
    try:
        uuid.UUID(candidate_uuid)
        return True
    except ValueError:
        pass
    return False


def close_connection_nothrow(connection):
    """
    Closes connection
    """
    try:
        if connection:
            connection.close()
    except:
        pass
