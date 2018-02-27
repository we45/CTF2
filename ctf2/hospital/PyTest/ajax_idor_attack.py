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
from results import log_results,log_exceptions,delete_index,display_results
from termcolor import *
from colorama import *
init(autoreset=True)

def ajax_idor(webdriver): 
    try:   
        webdriver.get(url + "/")   

        authenticate(webdriver,'betty.ross@we45.com','secdevops')

        time.sleep(2)
        
        webdriver.get(url + '/records/')

        login_cookie = webdriver.get_cookies()

        csrf_token = ''
        for b in login_cookie:
            if b.get('name') == "java_csrf":
                csrf_token = b.get('value')

        print colored("Harvesting CSRF token for AJAX request","cyan")
        token_val = csrf_token
        # print "CSRF",csrf_token
        # webdriver.execute_script("$(document).ready(function() {$.ajax({type: 'POST',url: /update/record/',data: {rid: 1,remarks :'AIDS',csrfmiddlewaretoken: '%s',},success: function(data) {alert(data);error: function(xhr, textStatus, errorThrown) {alert('something went wrong');alert(errorThrown)}});});"%csrf_token)
        print colored("Executing AJAX request to update patient record.......","cyan")

        # webdriver.execute_script("$.ajax({type: 'POST',url: '/update/record/',data: {rid: 4,remarks : 'Test Sugar Level',csrfmiddlewaretoken: '%s',},success: function(data) {alert(data);},error: function(xhr, textStatus, errorThrown) {alert('something went wrong');}});"%csrf_token)
        webdriver.execute_script("$.ajax({type: 'POST',url: '/update/record/',data: {rid: 4,remarks : 'Test Sugar Level',csrfmiddlewaretoken: '%s',},success: function(data) {alert('Success');},error: function(xhr, textStatus, errorThrown) {alert('something went wrong');}});"%csrf_token)

        print colored("Updated steve.jobs@we45.com's patient record", "red")
        # print is_alert_present(webdriver)
        if is_alert_present(webdriver):
            alert = webdriver.switch_to_alert()        
            time.sleep(3)
            # if str(alert.text) == "Succesfully updated test's Health Record.":
            if str(alert.text) == "Success":     
                # log_results('test_ajax','%s/update/record/'%url,'rid','AJAX IDOR','Success')
                log_results('test_ajax','%s/update/record/'%url,'rid','AJAX IDOR','Failure')
                print 'Test success'
            else:
                # log_results('test_ajax','%s/update/record/'%url,'rid','AJAX IDOR','Failure')
                log_results('test_ajax','%s/update/record/'%url,'rid','AJAX IDOR','Success')
                print 'Test failure'
            alert.accept()

        webdriver.get(url + "/logout")

        authenticate(webdriver,'steve.jobs@we45.com','secdevops')    

        webdriver.get(url + '/records/')

        time.sleep(3)

        print colored("IDOR using AJAX is exploited :)","red")

        # webdriver.close()
    except BaseException as e:
        log_exceptions(e)

def test_ajax(webdriver):
    delete_index()
    ajax_idor(webdriver)
    display_results()
           