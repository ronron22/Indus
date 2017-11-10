#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 3

import argparse
import sys
import pika
from subprocess import check_output, call

amqp_queue = 'pai'

parser = argparse.ArgumentParser(description="Editeur")
parser.add_argument('file_name', nargs='?', type=str, action="store", default="", help="file to load")
parser.add_argument('-v', '--version', action='store_true', default=False, help="Version du logiciel")
parser.add_argument('-l', '--list', action='store_true', default=False, help="liste de la queue")

# dictionnaire des arguments
dargs = vars(parser.parse_args())

# on associe la clef 'file_name' du dictionnaire dargs a la
# variable 'file_name'
file_name = dargs['file_name']

 
if dargs['version']:
    version()
    sys.exit()
 
def read_file(file_name):
    if not file_name :
        print("A file name is needed") 
        sys.exit()
    else:
        try:
            file_body = open(file_name,'r')
            return file_body.read()
        except:
            print("Unable to open %s" % file_name) 

def send_message(file_name,file_body):

    #define credential
    credentials = pika.PlainCredentials('pai', 'pai')

    try :
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'pai_vhost',credentials))
    except: 
        print("Unable to connect to ampq server") 
        sys.exit()

    try :
        channel = connection.channel()
    except: 
        print("Unable to open the channel") 
        sys.exit()

    # on declare une nouvelle queue sur le serveur
    try :
        channel.queue_declare(queue=amqp_queue)
    except: 
        print("Unable to declare queue %s" % file_name) 
        sys.exit()

    # on envoi le message 
    try :
        channel.basic_publish(exchange='',routing_key='pai',body=(file_body))
    except: 
        print("Unable to publish %s on pai" % (file_body)) 
        sys.exit()

    try :
        print " [x] Sent message"
    except: 
        print("Unable to print the status") 
        sys.exit()

    try :
        connection.close()
    except: 
        print("Unable to closed connection") 
        sys.exit()

def view_queue():
    current_id = check_output("/usr/bin/id -u", shell = True)
    if int(current_id) > 0 :
        print("You must be root to execute this command, you're real id is %s" % current_id) 
        sys.exit()
    else:
        print("Liste des messages en attentes") 
        call(["/usr/sbin/rabbitmqctl", "list_queues", "-p" ,"pai_vhost"])


if dargs['list']:
    view_queue()
    sys.exit()


send_message(file_name,(read_file(file_name)))
