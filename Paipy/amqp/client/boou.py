# on defini les param de la connexion
connection = pika.BlockingConnection(pika.ConnectionParameters(
'localhost',5672,'pai_vhost',credentials))

# on defini le canal
channel = connection.channel()

# on declare une nouvelle queue sur le serveur
channel.queue_declare(queue='hello')

# on envoi le message 
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print " [x] Sent 'Hello World!'"

connection.close()
