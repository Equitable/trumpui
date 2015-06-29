
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

from trump import SymbolManager

es = Elasticsearch([{'host': 'localhost', 'port':9200}])
ic = IndicesClient([{'host': 'localhost', 'port':9200}])
sm = SymbolManager()

syms = sm.search()

mapping = {
            'properties': {
               'name': {'type': 'string', 'index': 'not_analyzed' },
               'tags': {'type': 'string', 'index': 'not_analyzed' },
               'description': {'type': 'string'},
               'meta' : {'type' : 'nested'}
            }
         }

if es.indices.exists(index='trump'):
    es.indices.delete(index='trump')

es.indices.create(index='trump')

es.indices.put_mapping(index='trump', doc_type='symbol', body=mapping)

for i, sym in enumerate(syms):
    print sym.name
    es.index(index='trump', doc_type='symbol', id=i, body=sym.to_json())


