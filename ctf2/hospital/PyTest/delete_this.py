from selenium.webdriver import Firefox
from selenium import webdriver
from pyvirtualdisplay import Display

driver = Display(visible=0, size=(800, 600))
driver.start
driver = Firefox()
driver.get('http://testfire.net')
driver.implicitly_wait(5)
print 'current url ->', driver.current_url