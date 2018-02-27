from selenium.webdriver import Firefox
import requests
url = "http://127.0.0.1:8000"
def sql_injection():
    print 'prakash'
    sql_session = requests.Session()
    login_url = url+ "/login/"
    login_page = sql_session.get(login_url)
    csrf_token = sql_session.cookies['java_csrf']
    print csrf_token
    
    
    

