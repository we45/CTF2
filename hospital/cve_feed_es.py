from elasticsearch import Elasticsearch
from lxml import etree

#es = Elasticsearch(['192.168.1.8'], http_auth = ('Sherlock,Watson'),port=9200, use_ssl=False)

es = Elasticsearch(['http://Sherlock:Watson@192.168.1.64:9200'])

if not es.indices.exists(index = 'nvd'):
    es.indices.create(index = 'nvd')

all_items = etree.parse('allitems.xml')

root = all_items.getroot()
print root

all_my_items = root.findall('item')

cve_object = {}

for item in all_my_items:
    cve_object = {}
    cve_id = item.get('name')
    cve_object['name'] = cve_id
    description = item.findtext('desc')
    cve_object['description'] = description
    all_refs = item.find('refs')
    reflist = [ref.text for ref in all_refs]
    cve_object['references'] = reflist
    
    print cve_object
    es.index(index='nvd', doc_type='cve', body = cve_object)
        
        
