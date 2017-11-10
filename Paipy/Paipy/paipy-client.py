#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import logging
import sys
import time
import coloredlogs
coloredlogs.install(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

file_handler = logging.FileHandler('/var/log/paipy/paipy-client.log', 'a')

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)

queue = redis.client.StrictRedis(host='213.218.154.197')

channel = queue.pubsub()

if len(sys.argv) > 1:
    argnb=0
    for arg in sys.argv: 
        if argnb > 0:
            if '-h' in arg:
                logger.info('Read the code please !!!')
                sys.exit()
            logger.info('Sending: '+arg)
            queue.publish('pai', arg)
        argnb += 1
else:
    logger.info('You must provide one argument :\'host name\'')
