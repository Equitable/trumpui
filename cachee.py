
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='trumpweb')

channel.basic_publish(exchange='',
                      routing_key='trumpweb',
                      body='ca_primerate')
print " [x] Told cacher to cache {}".format('ca_primerate')

connection.close()