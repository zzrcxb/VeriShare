import os
import urllib
import json

from pwShare.settings import DATA_PATH, RECAPTCHA_KEY
from random import sample
from hashlib import sha1 as hash_method
from functools import wraps


def passwd_generator(length):
    charset = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 122))
    passwd = ''
    for i in range(length):
        passwd += chr(sample(charset, 1)[0])
    return passwd


def save_file(file):
    h_obj = hash_method()
    list(map(h_obj.update, file.chunks()))
    hash_value = h_obj.hexdigest()
    fst = hash_value[:2]
    scd = hash_value[2:4]
    path = os.path.join(DATA_PATH, fst, scd)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, hash_value), 'wb') as f:
        list(map(f.write, file.chunks()))

    return hash_value

def verify_recaptcha(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        url = 'https://www.google.com/recaptcha/api/siteverify'
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = dict(secret=RECAPTCHA_KEY, response=recaptcha_response)
            data = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            if result.get('success', None):
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False

        return func(request, *args, **kwargs)
    return decorator


bot_alerts = [
    'Hey! Are you a bot trying to scrap my site?',
    'DO NOT submit too fast',
    'Was your mouse broken? Why did you click so fast?',
    'If you keeping submit too fast, you will be banned!'
]


prevable_list = [
    'application/atom+xml',
    'application/javascript',
    'application/json',
    'application/pdf',
    'application/xhtml+xml',
    'application/x-mpegURL',
    'application/x-rss+xml',
    'audio/flac',
    'audio/mpeg',
    'audio/mpegurl',
    'audio/ogg',
    'audio/x-ms-wma',
    'audio/x-pn-realaudio',
    'audio/x-wav',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/svg+xml',
    'image/tiff',
    'image/vnd.microsoft.icon',
    'image/x-ms-bmp',
    'image/x-photoshop',
    'message/rfc822',
    'text/css',
    'text/csv',
    'text/html',
    'text/richtext',
    'text/vcard',
    'text/vcard',
    'text/vnd.wap.wml',
    'text/vnd.wap.wmlscript',
    'text/x-vcalendar',
    'video/3gpp',
    'video/mpeg',
    'video/mp4',
    'video/quicktime',
    'video/ogg',
    'video/webm',
    'video/x-flv',
    'video/x-ms-wmv',
    'video/x-msvideo',
    'video/x-matriska',
]
