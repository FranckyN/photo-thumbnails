"""
    photo_processor_consumer
    ~~~~~~~~~~~~~
    Implements the image processing logic
    Business logic: Creates a RabbitMQ consumer that is listening on the
    photo-proccessor queue, processing one message at a time.
    copyright: ©2019 by Franck Nassé
"""
import os
import pika
import uuid
import time
import photo_processing as pp
import logging
import apps_logger as apl
import apps_utils as apu


def Logger():
    return logging.getLogger('photo_processor')


apl.configure_logger(Logger())


def consume():
    """
    Rabbit MQ consumer
    """
    try:
        connect_to_rabbitmq()
    except Exception as error:
        Logger().error(str(error))


def connect_to_rabbitmq():
    """
    Connects to RabbitMQ and waits for new messages.
    """
    queue_name = 'photo-proccessor'
    max_retry = 100
    curr_retry = 0
    while curr_retry < max_retry:
        connection = None
        try:
            Logger().info("connecting to rabbitmq...")
            parameters = pika.URLParameters(os.environ['AMQP_URI'])
            curr_retry += 1
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name,
                                  on_message_callback=consumer_handler)
            channel.start_consuming()
        except Exception as error:
            Logger().error(str(error))
        finally:
            apu.close_connection_nothrow(connection)
        time.sleep(20)
    message_critical = ("closing application after {} connection "
                        "attempts to rabbitmq broker")      
    Logger().critical(message_critical.format(curr_retry))


def consumer_handler(ch, method, properties, body):
    """
    Rabbit MQ consumer handler
    body should contain a valid uuid
    """
    Logger().info("Consumer has received {}".format(body))
    current_uuid = str(uuid.UUID(body.decode()))
    pp.photo_processing_update_db(current_uuid)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    Logger().info("message {} acknowledged".format(body))


if __name__ == '__main__':
    consume()
