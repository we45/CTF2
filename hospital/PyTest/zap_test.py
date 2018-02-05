import sys
reload(sys)
sys.setdefaultencoding('UTF8')
import pytest
import json
import base64
from datetime import datetime
from termcolor import *
from colorama import *
init(autoreset=True)
from results import log_results,log_exceptions,delete_index,display_results
from elasticsearch import Elasticsearch
from zap_wrapper import ZAPScanner
from fixtures import url
from hospital import settings

def scan_zap():
	try:
		es = Elasticsearch()
		init_es = {}

		init_es['vulnerability'] = {}		
		
		# new = ZAPScanner(target,scan_policy='Really Light',authentication_script='sarpastra_new.scripts.TestfireAuthScript')	
		new = ZAPScanner(settings.SYSTEM_IP,scan_policy='Really Light')	
		new.run()
		data = new.get_results()
		json_db = json.dumps(data, indent=4)
		vul_data = json.loads(json_db)
		severity_dict = {
			'Low':1,
			'Medium':2,
			'High':3,
			'Information':0,
			'Info':0,
		}
		for k,v in vul_data.items():
			alert = v.get('alert')			
			if isinstance(alert, dict):
				std_es = init_es				
				std_es['vulnerability'] = {
					'tool' : 'ZAP',
					'name' : alert.get('alert','Unknown'),
					'created_on' : datetime.now().strftime("%Y-%m-%d"),
					'description' : alert.get('description',''),
					'remediation' : alert.get('solution',''),
					'severity' : severity_dict.get(alert.get('risk','Info'),0)
				}	
				
				request_string = "%s%s" % (v.get('requestHeader',''), v.get('requestBody',''))
				response_string = "%s%s" % (v.get('responseHeader',''), v.get('responseBody',''))				 
				cwe = v.get('cweid')
				if cwe:
					std_es['vulnerability']['cwe'] = {
						'cwe_id' : cwe,
						'cwe_link' : 'https://cwe.mitre.org/top25/index.html#CWE-%s'%cwe
					}					
				std_es['vulnerability']['app_param'] = {
					'param_name' : alert.get('param',''),
					'param_url' : alert.get('url',''),
					'param_request' : base64.b64encode(request_string),
					'param_response' : base64.b64encode(response_string)
				}				
				std_es['vulnerability']['evidences'] = {
					'log' : base64.b64encode(alert.get('evidence',''))
				}
				es.index(index = 'ctf', doc_type = 'zap_docs', body = std_es)
		# print 'Docs created'					
		print 'Scan completed'					
	except BaseException as e:
		# print e
		log_exceptions(e)

def test_zap():	
	delete_index()
	scan_zap()
	display_results()
