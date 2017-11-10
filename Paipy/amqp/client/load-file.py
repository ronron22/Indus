import sys
import pika

	

print type(sys.argv)
print len(sys.argv)

if len(sys.argv) > 1 : 
	for arg in sys.argv :	
		print sys.argv.index(arg)
		if sys.argv.index(arg) == 1:
			file_name = arg

			file_body = open(file_name,'r')
			

else:
	print("met un argument bidon") 
	sys.exit()


def send_message(file_name):

	# define credential
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
		channel.queue_declare(queue=file_name)
	except: 
		print("Unable to declare queue %s" % file_name) 
		sys.exit()

	# on envoi le message 
	try :
		channel.basic_publish(exchange='',routing_key=file_name,body=(file_body.read()))
	except: 
		print("Unable to publish %s on %s" % (file_body,file_name)) 
		sys.exit()

	try :
		print " [x] Sent message"
	except: 
		print("Unable to print the status") 
		sys.exit()

	try :
		connection.close()
	except: 
		print("Unable to closed connectionr") 
		sys.exit()
