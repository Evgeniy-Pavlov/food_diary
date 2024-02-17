import datetime
import json
from browser import document, ajax, bind, session_storage, local_storage, html
from base import URL


login_form = html.FORM()

def set_data_in_storage(request):
    if request.status == 200:
        data = request.json
        local_storage.storage['user_id'] = data['id']
        local_storage.storage['email'] = data['email']


def get_userinfo(access_token):
    req = ajax.Ajax()
    username = local_storage.storage['username']
    headers_data = {'Content-Type': 'application/json', 'Accept': '*/*', 'Authorization': f'Bearer {access_token}'}
    url = f'{URL}/api/user/userinfo?username={username}'
    document['request-result'].text = url
    result = ajax.get(url, mode="json", oncomplite=set_data_in_storage, headers = headers_data)
    

def complete_request(request):
    if request.status == 200:
        data = request.json
        session_storage.storage['access'] = data['access']
        session_storage.storage['refresh'] = data['refresh']
        get_userinfo(session_storage.storage['access'])
        document <= html.DIV('Success auth! <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',\
            Class='alert alert-success alert-dismissible fade show position-absolute top-0 start-50', role='alert')
        #document['request-result'].text = data
    elif request.status == 401:
        document <= html.DIV('Invalid username or password! <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',\
            Class='alert alert-warning alert-dismissible fade show position-absolute top-0 start-50', role='alert')
    else:
        document <= html.DIV('Server error!!! <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',\
            Class='alert alert-danger alert-dismissible fade show position-absolute top-0 start-50', role='alert')


@bind('#login-btn', 'click')
def click(event):
    req = ajax.Ajax()
    username = document['loginInputUsername'].value 
    password = document['loginInputPwd'].value
    req.bind('complete', complete_request)
    req.open('POST', f'{URL}/api/auth', True)
    req.set_header('Content-Type', 'application/json')
    req.set_header('Accept', '*/*')
    req.set_header('Accept-Language', 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7')
    data = {'username': username,'password': password}
    req.send(json.dumps(data))
    local_storage.storage['username'] = username

