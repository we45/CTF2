from zapv2 import ZAPv2
import socket
import subprocess
import os
import time
import importlib
from hospital import settings


class ZAPScanner(object):
    '''
    This is the object that will be used to launch and control the ZAP Scans. This will perform all the scans against authenticated
    and unauthenticated targets.
    Mandatory params:
        - param: target => target url or IP with scheme and protocol    

    Optional Params
        - param: authentication_script => Will support Python Scripts with Selenium    
        - param: scan_policy => name of the scan policy that will be used to run the ZAP Daemon
        - param: api_key => The API Key used by ZAP for authenticating requests to ZAP.

    KNOWN BUGS
        - Currently, there is no support for targets that have a non-standard port. i.e. targets like http://google.com:9000

    '''

    def __init__(self, target, authentication_script = None, scan_policy = 'Default', api_key = None):
        try:
            self.target = target            
        except ValueError:
            print 'No or incorrect target. Please add a correct target'
        self.zap_host = settings.ZAP.get('ip')
        self.zap_port = settings.ZAP.get('port')
        self.authentication_script = authentication_script        
        self.scan_policy = scan_policy
        self.api_key = api_key
        self.params = None
        self.results = None


    def prlog(self,statement):
        print '[ + ] %s ' % statement


    def run(self):
        '''

        This is the class function that will be invoked while running a zap scan.

        This will first run zap.sh wherever installed. Subsequently, this will run any authentication scripts if any.
        Subsequently, this will run the zap scan with spider, etc.

        Returns:
            - JSON Payload with scan results.

        TODO:
            - Separate the following functions: running ZAP, running auth scripts, and indexing results
            - Implement psmonitor to check for zap process already loaded

        '''

        
        self.prlog('Starting ZAP as daemon')   
        time.sleep(30)     

        scan = ZAPv2(proxies={'http': 'http://%s:%s' % (self.zap_host, self.zap_port), 'https': 'https://%s:%s' % (self.zap_host, self.zap_port)})
        # print scan
        if self.authentication_script:
            self.run_authentication_script()
        
        scan.urlopen(self.target)

        time.sleep(2)

        self.prlog('Running Spider against target %s' % self.target)

        scan_spider = scan.spider.scan(self.target)

        self.prlog('Waiting for 10 seconds for spider to run')
        
        while int(scan.spider.status) < 100:
            self.prlog('Spidering target at %s' % str(scan.spider.status))
            time.sleep(10)

        self.prlog('Spider completed.')

        self.prlog('Commencing Active Scan on the target...')

        scan_ascan = scan.ascan.scan(self.target)
        time.sleep(5)

        while int(scan.ascan.status) < 100:
            self.prlog('Scanning target at %s' % str(scan.ascan.status))
            time.sleep(10)             

        db = {}        
        for alert in scan.core.alerts():
            num_messageId = int(alert['messageId'])
            db[num_messageId] = scan.core.message(num_messageId)
            db[num_messageId]['alert'] = scan.core.alert(num_messageId)

        # The results variable is set here.
        self.results = db

        scan.core.shutdown()


    def get_results(self):
        '''
        Function is used to fetch the results. The params dict and the alerts and messages are retrieved as a tuple of dictionaries
        Returns:
            - Tuple of dictionaries for processing
        '''

        return self.results



    def run_authentication_script(self):
        '''

        This function runs an authentication script for the ZAP Scanner. In many cases, zap will not be able to authenticate using
        the standard auth module. Therefore, we will use importlib to import a specific script that we will use to run the script.

        All the params required for the script will be passed by our lib

        Returns:
            - Some signal that the script has run

        '''
        self.prlog('Running Authentication Script....')        
        mymodule = importlib.import_module(self.authentication_script)
        mycl = getattr(mymodule, ''.join(self.authentication_script.rsplit('.',1)[1:]))
        script_obj = mycl(proxy_host = self.zap_host, proxy_port = self.zap_port, target = self.target)
        script_obj.run_script()












