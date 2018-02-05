import pytest
from selenium.webdriver import Firefox
import time
from fixtures import webdriver,url,authenticate
from termcolor import *
from results import log_results,log_exceptions,delete_index,display_results


def session_fixation(webdriver, email = 'steve.jobs@we45.com'):
    try:
        authenticate(webdriver,username=email)
        post_auth_cookie = webdriver.get_cookies()
        print colored('- Cookie after login: {0}'.format(post_auth_cookie), 'yellow')
        webdriver.find_element_by_link_text(email).click()
        webdriver.find_element_by_link_text("Log Out").click()
        print colored('- Logging out as user: {0}'.format(email),'yellow')    

        webdriver.delete_all_cookies()
        for c in post_auth_cookie:
            webdriver.add_cookie(c)
        time.sleep(5)
        after_set_cookie = webdriver.get_cookies()
        print colored('- Cookie after setting: {0}'.format(after_set_cookie), 'green')

        load_url = '%s/dashboard/'%url
        webdriver.get(load_url)    
        time.sleep(10)
        if load_url == webdriver.current_url and after_set_cookie[0].get('value') == post_auth_cookie[0].get('value'):        
            log_results('test_session_fixation','%s/dashboard/'%url,'sessionid','Session Fixation','Success')
            print 'Test success'
        else:
            log_results('test_session_fixation','%s/dashboard/'%url,'sessionid','Session Fixation','Failure')
            print 'Test failure'
    except BaseException as e:
        log_results('test_session_fixation','%s/dashboard/'%url,'sessionid','Session Fixation','Failure')
        log_exceptions(e)

def test_session_fixation(webdriver):
    delete_index()
    session_fixation(webdriver, email = 'steve.jobs@we45.com')
    display_results()

    

