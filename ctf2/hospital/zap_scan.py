from zapv2 import ZAPv2
import time
import subprocess
import pprint
import os
from elasticsearch import Elasticsearch
from datetime import datetime
import base64
from base64 import b64encode
import json
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')
from selenium.webdriver import Firefox, FirefoxProfile
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import ProxyType,Proxy
from results import log_results, log_exceptions, delete_index, display_results
from ctf_selenium import *



#CI/CD Demo

def zap_docker():
    try:
        print '[+] Starting ZAP'
        cmd = '/home/prakash/bit_bucket/ctf2/hospital/ZAP_2.5.0/zap.sh -daemon -config api.disablekey=true -port 8090'
        subprocess.Popen(cmd.split(' '), stdout=open(os.devnull, 'w'))
        time.sleep(20)
        zap = ZAPv2(proxies={'http': 'http://%s:%s' % ('127.0.0.1', '8090'),
                             'https': 'https://%s:%s' % ('127.0.0.1', '8090')
                             })
        run_all()
        # pprint.pprint(zap.core.alerts())
        # print '___________________________________________________________________________'

        db = {}

        for alert in zap.core.alerts():
            num_messageId = int(alert['messageId'])
            db[num_messageId] = zap.core.message(num_messageId)
            db[num_messageId]['alert'] = zap.core.alert(num_messageId)
        results = db

        es = Elasticsearch()
        init_es = {}
        init_es['vulnerability'] = {}
        data = results
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
                    'param_response' : base64.b64encode(str(response_string))
                }               
                std_es['vulnerability']['evidences'] = {
                        'log' : base64.b64encode(alert.get('evidence',''))
                }
                es.index(index = 'ctf', doc_type = 'zap_docs', body = std_es)
        # print 'Docs created'                  
        print '[+] Scan completed'
        zap.core.shutdown()
    except BaseException as e:
        # print e
        log_exceptions(e)
        zap.core.shutdown()

# def test_zap(): 
#     delete_index()
#     zap_docker()
#     display_results()
delete_index()
zap_docker()
display_results()