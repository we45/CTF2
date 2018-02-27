from selenium.webdriver import Firefox, FirefoxProfile
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import ProxyType,Proxy
profile = FirefoxProfile()
profile.set_preference("network.proxy.type", 1)
profile.set_preference("network.proxy.http", "127.0.0.1")
profile.set_preference("network.proxy.http_port", 8080)
profile.set_preference("network.proxy.noProxy", '')
profile.update_preferences()

myProxy = "localhost:8090"

proxy1 = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': myProxy,
    'ftpProxy': myProxy,
    'sslProxy': myProxy,
    'noProxy': '' # set this value as desired
})
# driver = Firefox(profile)
driver = Firefox(profile,proxy=proxy1)
#driver = Firefox()
driver.maximize_window()
driver.implicitly_wait(30)
url = 'http://127.0.0.1:8000'

def run_all():
    print 'Running the Selenium Script'
    driver.get('%s' % url)
    print '[+] ' + driver.current_url
    driver.implicitly_wait(5)
    # Clicks on 'About'
    driver.get('%s/about/' % url)
    print '[+] ' + driver.current_url
    driver.get('%s/appointment/add/' % url)
    print '[+] ' + driver.current_url
    driver.implicitly_wait(5)
    # Name
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[1]/div[1]/div/div/input').clear()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[1]/div[1]/div/div/input').send_keys('selenium test')
    driver.implicitly_wait(5)
    # Phone number
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[2]/div[1]/div/div/input').clear()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[2]/div[1]/div/div/input').send_keys('0011223344')
    driver.implicitly_wait(5)
    # Gender
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[3]/div[1]/div/div/select').click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[3]/div[1]/div/div/select/option[2]').click()
    driver.implicitly_wait(5)
    # Health Plan
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[4]/div[1]/div/div/select').click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[4]/div[1]/div/div/select/option[3]').click()
    driver.implicitly_wait(5)
    # Select Health Plan
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[5]/div[1]/div/div/select').click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[5]/div[1]/div/div/select/option[2]').click()
    driver.implicitly_wait(5)
    # Appointment reason
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[6]/div[1]/div/div/textarea').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[6]/div[1]/div/div/textarea').send_keys('Selenium Test')
    # Email
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[1]/div[2]/div/div/input').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[1]/div[2]/div/div/input').send_keys('selenium@test.com')
    driver.implicitly_wait(5)
    # Date of Birth
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[2]/div[2]/div/div/input').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[2]/div[2]/div/div/input').send_keys('2/4/2017')
    driver.implicitly_wait(5)
    # Address
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[3]/div[2]/div/div/textarea').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[3]/div[2]/div/div/textarea').send_keys('Selenium Test')
    driver.implicitly_wait(5)
    # Appointment Date
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[5]/div[2]/div/div/input').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[5]/div[2]/div/div/input').send_keys('2/4/2017')
    driver.implicitly_wait(5)
    # Submit
    driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[7]/div/div/input').click()
    driver.implicitly_wait(5)
    time.sleep(10)
    driver.get('%s/contact_us/' % url)
    print '[+] ' + driver.current_url
    time.sleep(10)
    driver.get('%s/login/' % url)
    print '[+] ' + driver.current_url
    time.sleep(10)
    driver.find_element_by_xpath('/html/body/div/div/section/form/div[1]/input').clear()
    driver.find_element_by_xpath('/html/body/div/div/section/form/div[1]/input').send_keys('bruce.banner@we45.com')
    driver.find_element_by_xpath('/html/body/div/div/section/form/div[2]/input').clear()
    driver.find_element_by_xpath('/html/body/div/div/section/form/div[2]/input').send_keys('secdevops')
    driver.find_element_by_xpath('/html/body/div/div/section/form/div[3]/button').click()
    time.sleep(10)
    print '[+] ' + driver.current_url
    driver.implicitly_wait(10)
    time.sleep(10)
    print '[+] ' + driver.current_url
    driver.get('%s/technicians/' % url)
    time.sleep(10)
    print '[+] ' + driver.current_url
    driver.get('%s/appointment/plan' % url)
    time.sleep(10)
    print '[+] ' + driver.current_url
    driver.get('%s/appointment/doctor' % url)
    time.sleep(10)
    print '[+] ' + driver.current_url
    driver.get('%s/secure_tests/' % url)
    time.sleep(10)
    # Sends keys and clicks on 'Search'
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/form/div/input[1]').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/form/div/input[1]').send_keys('selenium test')
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/form/div/input[2]').click()
    driver.implicitly_wait(5)
    print '[+] ' + driver.current_url
    driver.get('%s/tests/' % url)
    time.sleep(10)
    # Sends keys and clicks on 'Search'
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/form/div/input[1]').clear()
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/form/div/input[1]').send_keys('selenium test')
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/form/div/input[2]').click()
    driver.implicitly_wait(5)
    print '[+] ' + driver.current_url
    driver.get('%s/plans/' % url)
    time.sleep(10)
    print '[+] ' + driver.current_url
    driver.get('%s/password_change' % url)
    time.sleep(10)
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[1]/div[2]/div/div/input').send_keys('secdevops')
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[2]/div[2]/div/div/input').send_keys('secdevops')
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[3]/button').click()
    driver.implicitly_wait(5)
    print '[+] ' + driver.current_url
    driver.get('%s/password_change_secure' % url)
    time.sleep(10)
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[1]/div[2]/div/div/input').send_keys('secdevops')
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[2]/div[2]/div/div/input').send_keys('secdevops')
    driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[2]/form/div[3]/button').click()
    driver.implicitly_wait(5)
    print '[+] ' + driver.current_url
    driver.get('%s/logout/' % url)
    driver.quit()
