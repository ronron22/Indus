#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika
import logging

from logging.handlers import RotatingFileHandler

# to file
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# stdout 
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)


logger.info('Hello')

def on_message(channel, method_frame, header_frame, body):
    print method_frame.delivery_tag
    print body
    print
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


credentials = pika.PlainCredentials('pai','pai')
logger.info('Opening connection with amqp server')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'pai_vhost',credentials))
logger.info('Opening connection with channel')
channel = connection.channel()

logger.info('Opening "pai" queue')
channel.basic_consume(on_message, 'pai')


try:
    logger.info('Starting consume queue')
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    logger.info('Unable to consume queue, exit')
connection.close()
