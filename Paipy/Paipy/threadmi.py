#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import time
import threading


def callback():
    r = redis.client.StrictRedis()
    sub = r.pubsub()
    sub.subscribe(['pai'])
    while True:
        for m in sub.listen():
            print m # 'Recieved: {0}'.format(m['data']) 
            toto = str(m['data'])
def main():
    t = threading.Thread(target=callback)
    t.setDaemon(True)
    t.start()
    while True:
        print 'Waiting'
        time.sleep(3)

if __name__ == '__main__':
    main()

