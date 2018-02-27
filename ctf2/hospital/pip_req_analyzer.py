from elasticsearch import Elasticsearch
import pprint
from fabric.api import *
from StringIO import StringIO
from jinja2 import Environment, FileSystemLoader
import os

es = Elasticsearch(['http://127.0.0.1:9200'])
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def query_struct(phrase):
    return {
      "query": {
        "match_phrase": {
          "description": phrase
          
        }
      }
    }

def getAndRenderTemplate(filename, nginxVars):
    jinja_env = Environment(loader=FileSystemLoader(THIS_DIR))
    tmpl = jinja_env.get_template(filename)
    # print tmpl.render(nginxVars)
    return StringIO(tmpl.render(nginxVars))

final_cves = []

with open('all_requirements.txt','r') as reqfile:
    for req in reqfile.readlines():
        d = {}
        str_req = req.split('==')[0].rstrip()
        #print str_req
        
        results = es.search(index = 'nvd', doc_type='cve', body = query_struct(str_req))
        #pprint.pprint(results['hits']['hits'])
        d[str_req] = results['hits']['hits']
        final_cves.append(d)

html_file_io = getAndRenderTemplate('cve.html', {'cves': final_cves})
html_file = open('cve_report.html', 'wb')
html_file.write(html_file_io.getvalue())
html_file.close()

import webbrowser
webbrowser.open('cve_report.html')



        #pprint.pprint(results)
#pprint.pprint(d)

#put(getAndRenderTemplate('cve.html', {
    #'app_name': vars.app_name,
    #'lport': vars.lport,
    #'dport': vars.dport,
    #'server_name': vars.server_name,
    #'d_user': vars.d_user
    #}), '/etc/nginx/sites-enabled/hello_nginx')


#results = es.search(index = 'nvd', doc_type='cve', body = query_struct('Django 1.4.6'))
#print results

