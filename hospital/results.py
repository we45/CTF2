from elasticsearch import Elasticsearch
from jinja2 import Environment, FileSystemLoader
import os
import webbrowser
import time
import json
# ['http://Sherlock:Watson@localhost:9200']
def get_es():
	return Elasticsearch()

def delete_index():
	es = get_es()
	if es.indices.exists(index = 'ctf'):
		es.indices.delete(index = 'ctf')

def log_results(test_name,url,parameter,vul,status):
	result_dict = {
		'test_name':test_name,
		'url':url,
		'parameter':parameter,
		'vulnerability':vul,
		'status':status
	}
	es = get_es()
	es.index(index = 'ctf', doc_type='vul_docs', body = result_dict, request_timeout=60)

def log_exceptions(e):
	print 'Breaking test due to exception'

def get_sev_query(sev):
    return {
        "_source": {
            "include": ["vulnerability"],
            "exclude": ["scan_work", "project"]
        },
        "size":10000,
        "query": {
            "bool": {
                "must": [                        
                    {
                        "match": {
                            "vulnerability.severity": {
                                "query": int(sev)
                            }
                        }
                    }
                ]
            }
        }
    }


def get_msearch_query():
    search_list = []
    for sev in [0,1,2,3,4]:
        search_list.append({'index': 'ctf', 'type': 'zap_docs'})
        search_list.append(get_sev_query(sev))     
    request = ''
    for each in search_list:
        request += '%s \n' %json.dumps(each)
    return request	

def get_status_count(es,status):
	query = {"size":0,"query":{"match_phrase":{"status":status}}}
	res = es.search(index = 'ctf', doc_type='vul_docs', body = query)
	return res['hits']['total']


from collections import Counter
import itertools
from operator import itemgetter
def display_results():
	j2_env = Environment(loader=FileSystemLoader(os.getcwd()), trim_blocks=True)
	es = get_es()
	if es.indices.exists(index = 'ctf'):
		query = {"size":10000,"query":{"match_all":{}}}
		data = es.search(index = 'ctf', doc_type='vul_docs', body = query)

		results = [d['_source'] for d in data['hits']['hits']]
		zap_data = es.msearch(body=get_msearch_query())
		resp = zap_data['responses']
		info,low,medium,high,critical = (0,1,2,3,4)
		info_dict = {key: list(group) for key, group in itertools.groupby(resp[info]['hits']['hits'], key=lambda i:i['_source']['vulnerability']['name'])}
		low_dict = {key: list(group) for key, group in itertools.groupby(resp[low]['hits']['hits'], key=lambda i:i['_source']['vulnerability']['name'])}
		medium_dict = {key: list(group) for key, group in itertools.groupby(resp[medium]['hits']['hits'], key=lambda i:i['_source']['vulnerability']['name'])}
		high_dict = {key: list(group) for key, group in itertools.groupby(resp[high]['hits']['hits'], key=lambda i:i['_source']['vulnerability']['name'])}
		critical_dict = {key: list(group) for key, group in itertools.groupby(resp[critical]['hits']['hits'], key=lambda i:i['_source']['vulnerability']['name'])}

		zap_results = {
			"info":info_dict,
			"low":low_dict,
			"medium":medium_dict,
			"high":high_dict,
			"critical":critical_dict,
		}
		counts = {
            "info":len(info_dict),
            "low":len(low_dict),
            "medium":len(medium_dict),
            "high":len(high_dict),
            "critical":len(critical_dict),
        }
		context = {
			'results':results,
			'zap_results':zap_results,
			'tool':'ZAP',
			# 'sevs':counts.keys(),
			'counts':counts,
			'passed': get_status_count(es,'Success'),
			'failed': get_status_count(es,'Failure')
		}
		file_data = j2_env.get_template('result_template.html').render(context)    
		f = open("results.html", 'w')
		f.write(file_data)
		f.close()
		filepath = os.path.join(os.getcwd(),'results.html')
		webbrowser.open(filepath)
	else:
		print 'Index not present'

   
	