#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
attention, une connexion établie dans une boucle
peut dévorer tous les sockets disponibles
"""

import redis
import time
import threading
import requests
import logging
from logging.handlers import RotatingFileHandler
import json
import os
from libpaipy.paipy_paipy3 import PaipyLib
from libpaipy.paipy_ansible import PaipyAnsible

import ansible
from ansible.playbook import PlayBook
from ansible.inventory import Inventory
from ansible import callbacks
from ansible import utils
import sys
import socket


""" ca bug ...
from jsonklog.handlers import ElasticSearchHandler
from jsonklog.formatters import JSONFormatter
from jsonklog.formatters import JSONFormatterSimple
"""

import coloredlogs
coloredlogs.install(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

file_handler = RotatingFileHandler('/var/log/paipy/paipy.log', 'a', 1000000, 1)

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

""" ca bug ...
es_handler = ElasticSearchHandler()
es_handler.setFormatter(JSONFormatter())
logger.addHandler(es_handler)
"""


my_time = int(time.time())

ansible_host_file = '/home/ansible/ansible/production/host-'
playbook_file = '/home/ansible/ansible/site.yml'
private_key = '/home/ansible/.ssh/install'

pubsub_period = 2
polling_active_period = 5 
getjson_period = 5
probing_period = 60
nb_ping = 5

host_vars=[
    'hostgroup_id',
    'environment_name',
    'ip',
    'name',
    'created_at',
    'hostgroup_name',
    'operatingsystem_name',
    'parameters',
    'mac',
    'owner_id',
    'build',
    'id'
]

"""
hostgroup_id: 9
environment_name: 
ip: u'172.16.81.200'
name: u'chopard7.host.net'
created_at: u'2015-02-19T16:04:43Z'
hostgroup_name:
operatingsystem_name
parameters: u'built_by_ansible
mac: u'00:50:56:9c:0b:98'
owner_id: 13
build: false
"""

"""
module ansible:
faire un keyscan pour peupler know_host :
ssh-keyscan pai-test1.host.net
sinon msg : FATAL: no hosts matched or all hosts have already failed -- aborting
"""

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

def list_queues(queues):
    rx = redis.client.StrictRedis(host='213.218.154.197')
    for queue in queues:
        try:
            if rx.exists(queue):
                logger.info('queue %s exist')
                try:
                    logger.info('queue %s : %s' % (queue,rx.llen(queue)))
                except:
                    logger.info('i don\'t no what this')
            else:
                logger.info('queue %s not exist' % queue)
        except:
                logger.info('queue %s not exist' % queue)
            
            

def pubsub_callback():
    th_name = threading.currentThread().getName()
    r1 = redis.client.StrictRedis(host='213.218.154.197')
    sub = r1.pubsub()
    sub.subscribe(['pai'])
    while True:
        time.sleep(pubsub_period)
        #list_queues('incoming')
        th_name = threading.currentThread().getName()
        #logger.info('%s have duration : %s' % (threading.currentThread().getName(),pubsub_period))
        logger.info('thread: %s - scruting pubsub queue' % th_name)
        for item in sub.listen():
            body = str(item['data'])
            if len(body) > 0: 
                logger.info('thread: %s body : %s' % (th_name,body))
                my_host_name = body 
                logger.info('thread : %s inserting %s on incoming' % (th_name,my_host_name))
                if 'host.net' in my_host_name :
                    r1.rpush('incoming', my_host_name )

                    t2 = threading.Thread(name='active callback', target=active_callback)
                    t2.setDaemon(True)
                    t2.start()
            else:
                logger.info('thread : ' + th_name + ' queue is empty')
                

def ansible_callback():
    th_name = threading.currentThread().getName()
    while True:
        time.sleep(getjson_period)
        #list_queues('active')
        #logger.info('%s have duration : %s' % (th_name, getjson_period))

        r  = redis.client.StrictRedis(host='213.218.154.197')

        my_obj = PaipyLib() 

        #status = []
        nb=0
        # on récupère toutes les entrées du hash 'active'
        if r.exists('active') and r.llen('active') > 0:
            logger.info('thread: %s - active lenght : %s' % (th_name, r.llen('active')))
            for host in r.lrange('active', 0 , 1):
                logger.info('thread: %s - host: %s' % (th_name, host))
                try:
                    #a = my_obj.loadjsonhost('https://userapi:userapi@foreman1.host.net/', host_vars, 'active', 2, host.rsplit('.')[0])
                    a = my_obj.loadjsonhost('https://userapi:userapi@foreman1.host.net/', host_vars, 'active', 2, host)
                except:
                    logger.info('thread: %s - nok - unable to obtain host info for %s' % (th_name, host))
                    r.lpop('active')
                    logger.info('thread: %s - nok - %s was popped from active' % (th_name, host))
                    r.lrem('deferred', 1, host)
                    r.lpush('deferred', host)
                    logger.info('thread: %s - nok - %s was pushed in deferred' % (th_name, host))
                    logger.info('thread: %s - nok - stopping thread for %s ' % (th_name, host))
                    break
                
                # on retire l'host d'active
                r.lpop('active')
                logger.info('thread: %s - keys was delete from active' % th_name)

                for key, value in a.items():
                    r.hset(host, key, value)
                    nb+=1

                # on tente de résoudre les noms
                logger.info('thread: %s - try to resolv %s' % (th_name, host))  
                hostslist = my_obj.hosts_resolv(host)
                if not host in hostslist:
                    logger.info('thread: %s - nok - unable to resolv ' % (th_name, host))
                    r.lrem('deferred', 1, host)
                    r.lpush('deferred', host)
                    break
                else:
                    logger.info('thread: %s - ok - resolving %s' % (th_name, host))


                """ bug
                si la machine n'est pas pinguable, le cas arrive lorsque le DNS pointe vers une IP privé
                """ 
                logger.info('thread: %s - waiting %s secondes before net probe' % (th_name, probing_period))  
                for i in range(probing_period, 0, -1):
                    logger.info('thread: %s - t-%s' % (th_name, i))
                    time.sleep(1)
                
                #time.sleep(probing_period)
                logger.info('thread: %s - try to ping %s' % (th_name, host))  
                hostslist = my_obj.netprobe(host, nb_ping)
                
                logger.info('thread: %s - hostslist: %s' % (th_name, hostslist)) 

                if not host in hostslist:
                    logger.info('thread: %s - nok - host %s unreachable, moving to deferred' % (th_name, host))
                    r.lrem('deferred', 1, host)
                    r.lpush('deferred', host)
                    break
                else:
                    logger.info('thread: %s - ok - host %s reachable' % (th_name, host))  
                    roles = r.hget(host, 'role') 
                    logger.info('thread: %s - using %s as roles' % (th_name, roles))  
                    j = my_obj.inventory_host_formating(ansible_host_file, host, roles,' site_name=std ansible_ssh_user=root proxy_on=pouet paipy=on')
                    logger.info('thread: %s - ok - writing host file' % th_name)  

    
                    logger.info('thread: %s - starting ansible for %s' % (th_name, host))
                    my_obj = PaipyAnsible()
                    #try:
                    my_obj.deploy(playbook_file, ansible_host_file+host, private_key) 
                    logger.info('thread: %s - nok - abnormal termination for ansible threads' % th_name)
                    r.lrem('delete', 1, host)
                    r.lpush('delete', host)
                    # except:
                    #     logger.info('thread: %s - ansible nok' % th_name)
                    #    r.lpush('deferred', host)
                    #    break

                    #logger.info('ansible : %s' % aa)

def active_callback():
    incoming = 'incoming'
    th_name = threading.currentThread().getName()

    while True:
        # je met le sleep car j'ai l'impression qu'il bouffe tous les sockets
        time.sleep(polling_active_period)

        #list_queues('incoming')
        #logger.info('%s have duration : %s' % (threading.currentThread().getName(),polling_active_period))
        r2 = redis.client.StrictRedis(host='213.218.154.197')
        for i in r2.lrange(incoming, 0, 1):
            my_id_number = r2.lpop(incoming)
            logger.info('thread: %s - %s have %s as score' % (th_name,i,my_id_number))
            time.sleep(3)
            logger.info('thread: %s - adding %s on active' % (i,th_name))
            r2.rpush('active', i)
            #print ('deleting %s on %s' % (i,incoming))
            #r2.(incoming,i)
    
            t3 = threading.Thread(name='ansible callback', target=ansible_callback)
            t3.setDaemon(True)
            t3.start()


def main():
    t = threading.Thread(name='pubsub callback', target=pubsub_callback)
    t.setDaemon(True)
    t.start()
    while True:
        #print 'main thread ...'
        time.sleep(2)

if __name__ == '__main__':
    main()

