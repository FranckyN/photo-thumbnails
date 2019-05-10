"""
    web_app_logic
    ~~~~~~~~~~~~~
    Implements the business logic of the web app.
    copyright: ©2019 by Franck Nassé
"""
import os
import pika
import apps_utils as apu
import apps_db_manager as apdbm
import logging


def Logger():
    return logging.getLogger('web_app_logger')


def get_pending_photo():
    """
    Get all photos with pending status.
    """
    return apdbm.db_manager.get_photos_by_status('pending')


def submit_photo_for_processing(uuid_data):
    """
    Submits the photos (using the uuids) so they can later be processed.
    :param uuid_data list of uuids
    returns a list of dictionary object following the format below:
    {'uuid':'29ed9f47-8f7e-4a69-9187-bf0ade0c15b5','success':False/True}
    """
    data_set = set(uuid_data)
    results = []
    for client_uuid in data_set:
        Logger().debug("client_uuid = {}".format(client_uuid))
        submitting_result, error = photo_submit_task(client_uuid)
        results.append({"uuid": client_uuid, "success": submitting_result,
                       "error": error})
    return results


def photo_submit_task(client_photo_uuid: str) -> bool:
    """
    Submits a new task to the processing queue.
    The uuid submitted must be valid!
    :param client_photo_uuid uuid string of a photo
    returns True or False along with an error message, whether
    or not the task is submitted. E.g False, 'badly formatted uuid'
    """
    try:
        if not apu.is_string_uuid(client_photo_uuid):
            return False, 'badly formatted uuid.'
        photo_status = apdbm.db_manager.get_photo_status(client_photo_uuid)
        Logger().debug("photo_status = {}".format(photo_status))
        if not photo_status:
            return False, ("photo not found or "
                           "something is wrong with the database")
        elif photo_status != 'completed':
            to_process_notification('photo-proccessor', client_photo_uuid)
            return True, ''
        else:  # if the photo was already processed, the task is not submitted.
            return False, 'processing already completed.'
    except Exception as error:
        Logger().error(str(error))
    return False, 'unexpected error'


def to_process_notification(queue_name: str, client_photo_uuid: str) -> bool:
    """
    Sends a message to a simple rabbitmq queue.
    :param queue_name the name of the queue.
    :param client_photo_uuid uuid of the photo to be processed.
    """
    # This is a barebones implementation
    connection = None
    try:
        parameters = pika.URLParameters(os.environ['AMQP_URI'])
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
                             exchange='',
                             routing_key=queue_name,
                             body=client_photo_uuid,
                             properties=pika.BasicProperties
                             (
                              delivery_mode=2,
                              content_encoding='utf-8'
                             ))
        Logger().info("Sent {} to queue {}".format(client_photo_uuid,
                                                   queue_name))
    finally:
        apu.close_connection_nothrow(connection)
