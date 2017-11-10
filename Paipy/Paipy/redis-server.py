#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import logger
import sys
import time


r = redis.StrictRedis()
listener = r.pubsub()
listener.subscribe(['pai'])
for item in listener.listen():
    print(item)
    my_obj = str(item['data'])
    print(type(my_obj))
    if 'host.net' in my_obj :
        f = open('out', 'a')
        f.write('%s\n' % my_obj)
        f.close()

