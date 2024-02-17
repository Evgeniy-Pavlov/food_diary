import datetime
import json
from browser import document, ajax, bind, html
from base import URL


register_form = html.FORM()


def complete_request(request):
    if request.status == 201:
        data = request.json
        document <= html.DIV('User success created! <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',\
            Class='alert alert-success alert-dismissible fade show position-absolute top-0 start-50', role='alert')
    elif request.status == 400:
        document <= html.DIV('The user has already been created! <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',\
            Class='alert alert-warning alert-dismissible fade show position-absolute top-0 start-50', role='alert')
    else:
        document <= html.DIV('Server error!!! <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',\
            Class='alert alert-danger alert-dismissible fade show position-absolute top-0 start-50', role='alert')


@bind('#register-btn', 'click')
def click(event):
    req = ajax.Ajax()
    username = document['registerInputUsername'].value 
    email = document['registerInputEmail'].value 
    password = document['registerInputPwd'].value
    req.bind('complete', complete_request)
    req.open('POST', f'{URL}/api/register', True)
    req.set_header('Content-Type', 'application/json')
    req.set_header('Accept', '*/*')
    req.set_header('Accept-Language', 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7')
    data = {'username': username,'email': email, 'password': password}
    req.send(json.dumps(data))
    document['registerInputUsername'].value = ''
    document['registerInputEmail'].value = ''
    document['registerInputPwd'].value = ''
