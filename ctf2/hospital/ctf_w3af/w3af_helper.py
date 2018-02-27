from w3af_api_client import Connection, Scan
from w3af_api_client.traffic import Traffic
import time
import json
#import datetime
from datetime import datetime
from base64 import b64decode, b64encode
import requests
import time
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
# from custom_exceptions import StopScanException
import os
from mitm_proxy import we45MitmProxy
from CtfAuthScript import CtfAuthScript
from mitmproxy import controller, proxy
from mitmproxy.proxy.server import ProxyServer
import threading
from pyvirtualdisplay import Display	
from elasticsearch import Elasticsearch
import subprocess
from results import display_results, delete_index

CONSOLE_URL = os.environ.get('CONSOLE_URL', 'localhost')
CONSOLE_PORT = os.environ.get('CONSOLE_PORT', '8000')
TOTAL_CONSOLE_URL = 'http://{0}:{1}'.format(CONSOLE_URL, CONSOLE_PORT)
BASE64_PATH = os.environ.get('BASE64_PATH', '/home/prakash/bit_bucket/ctf2/hospital/ctf_w3af')
W3AF_HOST = os.environ.get('W3AF_HOST', 'localhost')
W3AF_PORT = os.environ.get('W3AF_PORT', '5000')
W3AF_PROFILE_PATH = os.environ.get('W3AF_PROFILE_PATH', '/home/prakash/bit_bucket/ctf2/hospital/ctf_w3af/w3af/profiles/')
W3AF_URL = 'http://{0}:{1}'.format(W3AF_HOST, W3AF_PORT)


def log_exception(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()    
    print "[+] Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)  


def make_console_request(json_val):
    try:
        # console_path = '{0}/api/push_results/'.format(TOTAL_CONSOLE_URL)
        # r = requests.post(console_path, json=json_val)
        es = Elasticsearch()
        es.index(index='ctf', doc_type='w3af_docs',body = json_val)
        # print 'Status Code from Console Response', #r.status_code
    except BaseException as e:
        log_exception(e)
        print "[+] Unable to make request to Console." 


class MITMThread(threading.Thread):
	def run(self):
		config = proxy.ProxyConfig(port=8090)
		server = ProxyServer(config)
		base64_path = os.path.join(BASE64_PATH,'output.base64')
		kwargs = {
			'ignore_ext': ('.jpg', '.js', '.jpeg', '.gif', '.png', '.xml', '.json', '.css', '.swf', 'svg', 'ico', '.cur'),
			'ignore_domain': ('mozilla', 'api.keen.io', '.woff')
		}        
		self.m = we45MitmProxy(server,base64_path,kwargs)
		self.m.run()

	def stop_mitm(self):
		self.m.shutdown() 
		self.m.load_data()

class SeleniumThread(threading.Thread):    
    def run(self):
    	# display = Display(visible=0, size=(800, 600))
    	# display.start()
    	s = CtfAuthScript()
    	s.run_script() 
    	# display.stop()


mycon = Connection(W3AF_URL, verbose = False)
print "[+] w3af Connection established with version %s" % (mycon.get_version()['version'])
scan = Scan(mycon)

def delete_finished_scans(scan_id):
	r = requests.delete('{0}/scans/{1}'.format(W3AF_URL,scan_id))
	if int(r.status_code) == 200:
		print '[+] Finished scans deleted'
	else:
		print '[+] Something went wrong while deleting the finished scans'

def run_scan_job(url):
	try:
		print '[+] Scan initiated'
		t1 = MITMThread() 	
		t2 = SeleniumThread()
		t1.start()
		t2.start()
		while t2.is_alive():
			pass
		else:
			t1.stop_mitm()
			profile_path = '{0}LatestSync1.pw3af'.format(W3AF_PROFILE_PATH)
			scan.start(open(profile_path).read(), [url])		
			time.sleep(20)
			while scan.get_status().get('is_running', False):
				# print 'Scan currently running'
				time.sleep(5)
			else:			
				write_to_es(scan.get_findings(),scan.scan_id)
				print '[+] Scan completed'
	except BaseException as e:
		log_exception(e)


severity_dict = {
    'Information':0,
    'Medium':2,
    'High':3,
    'Low':1,                
}  

def are_scans_running():
	r = requests.get('{0}/scans/'.format(W3AF_URL))
	if len(json.loads(r.content).get('items',0)):
		return True
	else:
		return False

def start_scan(target):     
    try:
        if are_scans_running():            
            print "[+] Error, scans are running"
        else:
        	run_scan_job(target)
    except BaseException as e:
        log_exception(e)       


def write_to_es(findings,scan_id):
	try:
		scan_urls = '{0}/scans/{1}/kb/'.format(W3AF_URL,scan_id)
		r = requests.get(scan_urls)
		ids = json.loads(r.text).get('items')
		unique_vuls = {i.get('name'):[] for i in ids}
		for j in ids:
			unique_vuls[j.get('name')].append(j.get('id'))
		for vuls in unique_vuls.values():
			init_es = {}
			init_es['vulnerability'] = {}
			std_es = init_es
			req_url = '{0}/scans/{1}/kb/{2}'.format(W3AF_URL,scan_id,vuls[-1])
			req = requests.get(req_url)
			req_value = json.loads(req.text)
			std_es['vulnerability'] = {
				'tool': 'w3af',
				'name': req_value.get('name', 'Unknown'),
				'created_on': datetime.now().strftime("%Y-%m-%d"),
				'description': req_value.get('long_description', ''),
				'remediation': req_value.get('fix_guidance', ''),
				'severity': severity_dict.get(req_value.get('severity', 'Information'))
			}
			#cwe = req_value.get('cwe_ids')
			#if cwe and isinstance(cwe,list) and len(cwe):           
				#std_es['vulnerability']['cwe'] = {
					#'cwe_id' : cwe[0],
					#'cwe_link' : 'https://cwe.mitre.org/top25/index.html#CWE-%s'%cwe[0]
				#}
			app_params = []
			for i in vuls:
				req_url = '{0}/scans/{1}/kb/{2}'.format(W3AF_URL,scan_id,i)
				req_value = json.loads(req.text)
				req_resp = requests.get('{0}{1}'.format(W3AF_URL,req_value.get('traffic_hrefs')[0]))
				req_json = json.loads(req_resp.text)
				std_es['vulnerability']['app_param'] = {
					'param_name': req_value.get('var', ''),
					'param_url': req_value.get('url', ''),
					'param_request': (req_json.get('request', '')),
					'param_response': (req_json.get('response', '')),
				}
				std_es['vulnerability']['evidences'] = {
					'log': req_value.get('evidence', '')
				}
				es = Elasticsearch()
				es.index(index = 'ctf', doc_type='w3af_docs', body = std_es, request_timeout=60)
				make_console_request(std_es)
	except BaseException as e:
		# print e
		log_exception(e)
	finally:
		delete_finished_scans(scan_id)


# subprocess.Popen('/home/nithin/PycharmProjects/ctf_w3af/w3af/w3af_api')
delete_index()
print '[+] Starting w3af'
time.sleep(10)
url = 'http://localhost:8000'
start_scan(url)
display_results()
