"""
    photo_processing
    ~~~~~~~~~~~~~
    Implements the image processing logic
    Business logic: downloading an image then resize it.
    copyright: ©2019 by Franck Nassé
"""
import os
import requests
from PIL import Image
from urllib.parse import urlparse
import tempfile
import apps_utils as apu
import apps_db_manager as apdbm
import logging


def Logger():
    return logging.getLogger('photo_processor')

class FileNotDownloadedException(Exception):
    """
    Custom exception raised if there in an issue with the requests.response
    """
    pass


def photo_processing_update_db(current_uuid):
    """
    Implements task 5 of the coding challenge
    1- Update db photos.status to processing.
    2- Download image using photos.url.
    3- Generate a thumbnail of max 320x320 dimensions,
    maintaining the aspect ratio.
    4- Store thumbnail file on mounted /waldo-app-thumbs directory.
    5- Store a new row on db table photo_thumbnails with the thumbnail details.
    For the photo_thumbnails.url just use the relative path to the file.
    6- On success, update photos.status to completed.
    7- On error, update photos.status to failed.
    """
    try:
        apdbm.db_manager.update_photo_status(current_uuid, 'processing')
        photo_url = apdbm.db_manager.get_photos_column(current_uuid, 'url')
        photo_details = {"uuid": current_uuid,
                         "url": photo_url, "height": 0, "width": 0}
        if download_process_photo(photo_url, photo_details):
            apdbm.db_manager.insert_new_thumbnail(photo_details)
            apdbm.db_manager.update_photo_status(current_uuid, 'completed')
            Logger().info("{} processing completed".format(current_uuid))
            return
    except Exception as error:
        Logger().error(str(error))
    apdbm.db_manager.update_photo_status(current_uuid, 'failed')


def download_process_photo(photo_url: str, photo_details) -> bool:
    """
    Downloads the image and generates a thumbnail. photo_details dict will also
    be updated with the location of the generated image.
    returns True or False depending on the success of the operations.
    """
    source_image = None
    try:
        image_name = urlparse(photo_url)
        image_name = os.path.basename(image_name.path)
        source_image = download_image(photo_url)
        destination_size, thumbnail_path = \
        generate_thumbnail(source_image, image_name,
                           os.environ['STORAGE_THUMBS'])
        Logger().info(" {} / {}".format(destination_size, thumbnail_path))
        temp_dict = {'url': os.path.relpath(thumbnail_path, os.getcwd()),
                     'width': destination_size[0], 'height': destination_size[1]}
        photo_details.update(temp_dict)
        return True
    except FileNotDownloadedException as error:
        details = error.args[0]
        Logger().error(str(details["response"]))
    except Exception as error:
        Logger().error(str(error))
    finally:
        if source_image:
            apu.remove_file(source_image)
            Logger().debug("deleted {}".format(source_image))
    return False


def download_image(image_url: str) -> str:
    """
    Downloads the image and returns its path on the local filesystem.
    """
    response = requests.get(image_url)
    if not response:
        error_message = "An error occurred while downloading {}"
        raise FileNotDownloadedException({"message": error_message. \
                                          format(image_url),
                                          "response": str(response)})
    temp_image_name = tempfile.mktemp()
    with open(temp_image_name, 'wb') as handler:
        handler.write(response.content)
    return temp_image_name


def generate_thumbnail(source_image_path: str,
                       image_name: str,
                       storage_directory: str):
    """
    Generates a thumbnail of max 320x320 dimensions,
    maintaining the aspect ratio.
    """
    im = Image.open(source_image_path)
    im.thumbnail((320, 320), Image.LANCZOS)
    destination_file = "{}/{}".format(storage_directory, image_name)
    Logger().debug("destination_file => {}".format(destination_file))
    im.save(destination_file, im.format) 
    return im.size, destination_file
