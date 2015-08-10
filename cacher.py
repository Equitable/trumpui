

from trump import SymbolManager

from equitable.db.psyw import SQLAeng
sme = SQLAeng('Trump','PROD')
sm = SymbolManager(sme)

import pika

credentials = pika.PlainCredentials('quants','quants')
rabbit = pika.ConnectionParameters(host='localhost',credentials=credentials)

connection = pika.BlockingConnection(rabbit)
channel = connection.channel()

channel.queue_declare(queue='trumpweb')

print ' Listening for instructions'

def callback(ch, method, properties, body):
    sm = SymbolManager()
    print str(ch)
    print str(method)
    print str(properties)
    print str(body)
    sym = sm.get(body)
    sym.cache()
    print "****"
    sm.finish()

channel.basic_consume(callback,
                      queue='trumpweb',
                      no_ack=True)

channel.start_consuming()