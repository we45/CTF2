import pytest
from selenium.webdriver import Firefox,Chrome
import time
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.proxy import Proxy,ProxyType
import os

url = 'http://{0}'.format(os.environ.get('WEB_SERVER','localhost'))

@pytest.fixture(scope='module')
def webdriver(request):
    # myProxy = "http://127.0.0.1:80"

    # proxy = Proxy({
    #     'proxyType': ProxyType.MANUAL,
    #     'httpProxy': myProxy,
    #     'ftpProxy': myProxy,
    #     'sslProxy': myProxy,
    #     'noProxy':''
    # })
    # driver = Firefox(proxy=proxy)
    driver = Firefox()
    driver.maximize_window()
    driver.implicitly_wait(30)
    def clear_all():
        # driver.get('%s/logout/'%url)
        driver.quit()
    request.addfinalizer(clear_all)
    return driver

# @pytest.fixture(scope='session')
# def webdriver(request):
#     # driver = Chrome('/home/nithin/chromedriver')
#     driver = Chrome()
#     driver.maximize_window()
#     driver.implicitly_wait(10)
#     request.addfinalizer(driver.quit)
#     return driver 

def is_alert_present(webdriver):
    try: webdriver.switch_to_alert()
    except NoAlertPresentException as e: return False
    return True      

def authenticate(webdriver,username='bruce.banner@we45.com',password='secdevops'):
    webdriver.get('%s/login/'%url)
    time.sleep(1)
    data = {'username': username, 'password': password}
    form = webdriver.find_element_by_tag_name('form')
    for k, v in data.items():
        elem = form.find_element_by_id("%s" % k)
        elem.clear()
        elem.send_keys(v)
    form.find_element_by_id('submit').click()
    webdriver.implicitly_wait(10)
    #assert 'dashboard' in webdriver.current_url




