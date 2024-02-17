import datetime
import json
from browser import document, ajax
from base import URL


def complete(request):
    data = request.json
    document["request-result"].text = data

def click(event):
    req = ajax.Ajax()
    req.bind('complete', complete)
    req.open('POST', f'{URL}/api/register', True)
    req.set_header('Content-Type', 'application/json')
    req.set_header('Accept', '*/*')
    req.set_header('Accept-Language', 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7')
    data = {'username': 'Ajax','email': 'test_ajax@mail.com', 'password': 'Qwerty123'}
    req.send(json.dumps(data))
    document["request-result"].text = "waiting..."

document["register-btn"].bind("click", click)