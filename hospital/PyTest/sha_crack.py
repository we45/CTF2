import pytest
from selenium.webdriver import Firefox
import time
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
from fixtures import webdriver,url,authenticate,is_alert_present
from selenium.common.exceptions import NoAlertPresentException,UnexpectedAlertPresentException
from selenium.webdriver.support.ui import Select
from datetime import datetime
from termcolor import *
from colorama import *
init(autoreset=True)

def test_sha1(webdriver):    
    try:
        webdriver.get(url + '/')
        webdriver.get(url + "/appointment/add/")            
        form = webdriver.find_element_by_tag_name('form') 
        date = datetime.today().strftime("%m/%d/%Y")
        # print date   
        # date = datetime.today()   
        form_data = {
            'input':{
                'name':'Test',
                'email':'test@test.com',
                'phone':'999999',  
                'reason':'Test',
                'address':'Test'                
            },
            'select':{
                'gender':'Male',
                'plan_type':'ConsultantAppointment',
                'doctor':'Bruce Banner'
            },
            'date':{
                'dob':'04/09/1991',
                'datetime':'%s'%date
            }
        }    
        for k,v in form_data.items():
            if k == 'input':
                for k1,v1 in v.items():
                    elem = form.find_element_by_id("id_%s"%k1)
                    elem.clear()
                    elem.send_keys(v1)
            elif k == 'select':
                for k1,v1 in v.items():
                    Select(form.find_element_by_id("id_%s"%k1)).select_by_visible_text(v1)
            elif k == 'date':
                for k1,v1 in v.items():
                    elem = form.find_element_by_id("id_%s"%k1)
                    elem.click()
                    elem.send_keys(v1)            
        
        form.find_element_by_xpath("//input[@value='Submit']").click()
        time.sleep(2)            
        shadata = webdriver.find_element_by_xpath("//div[@class='container']/input[@name='token']").get_attribute('value').encode('utf-8')
        data = shadata.split('$')
        hashedstring = data[2]
        print colored ("Identified a hashed string", 'green'), colored (hashedstring , 'magenta')
        print "\n"
        time.sleep(2)            
        hashfile = open('hashes.txt', 'w').close()
        hashfile = open('hashes.txt', 'a')
        hashfile.write(hashedstring+'\n')
        hashfile.close()
        fpath = os.path.abspath('hashes.txt')
        # print fpath
        john = "/home/secdevops/labs/john-1.7.9-jumbo-7/run/john"
        subprocess.call([john,'--format=raw-sha1', fpath])
        subprocess.call([john, '--format=raw-sha1', fpath, '--show'])
        time.sleep(2)            
    except BaseException, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)
           