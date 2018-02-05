import pytest
from selenium.webdriver import Firefox
import time
import requests
from requests.auth import HTTPBasicAuth
import json
from BeautifulSoup import BeautifulSoup
from fixtures import webdriver,url,authenticate,is_alert_present
from selenium.common.exceptions import NoAlertPresentException,UnexpectedAlertPresentException
from termcolor import *
from colorama import *
init(autoreset=True)
from results import log_results,log_exceptions,delete_index,display_results

def sql_injection():
    try:    
        sql_session = requests.Session()
        login_url = url + "/login/"
        get_login_page = sql_session.get(login_url)
        csrf_token = sql_session.cookies['java_csrf']

        login_data = dict(email_id='betty.ross@we45.com',password='secdevops',csrfmiddlewaretoken=csrf_token)
        login_request = sql_session.post(login_url, data=login_data, headers=dict(Referer=login_url))
        post_login_token = sql_session.cookies['java_csrf']
        test_url = '%s%s' % (url, '/tests/')
        status = False

        with open('SQL_payload.txt') as f:
            for payload in f.readlines():
                sqli_request = sql_session.post(test_url, data = dict(search = payload.rstrip(), csrfmiddlewaretoken=post_login_token), headers=dict(Referer=test_url))                
                soup = BeautifulSoup(sqli_request.text)
                result = soup('td')[1].text
                if result:
                    print colored('Payload ---> %s'%(payload),'red')
                    print colored('Result  ---> %s'%(soup('td')[1].text),'cyan')
                    status = True
                    break
        if status:
            log_results('test_sql_injection','%s/tests/'%url,'search','SQL Injection','Success')
            print 'Test success'
        else:
            log_results('test_sql_injection','%s/tests/'%url,'search','SQL Injection','Failure')
            print 'Test failure'
    except BaseException as e:
        log_results('test_sql_injection','%s/tests/'%url,'search','SQL Injection','Failure')
        log_exceptions(e)

def test_sql_injection():
    delete_index()
    sql_injection()
    display_results()
