import os
import urllib
import json
import uuid
import time

from django.http import JsonResponse
from pwShare.settings import DATA_PATH, RECAPTCHA_KEY, TMP_PATH
from random import sample
from hashlib import sha1 as hash_method
from functools import wraps
from .settings import REFER_PROTECTOR
from urllib.parse import urlparse


def refer_limitation(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        refer = request.META.get('HTTP_REFERER', '')
        hostname = urlparse(refer).netloc
        print(REFER_PROTECTOR.records, hostname)
        if len(hostname) == 0:
            pass
        elif hostname in REFER_PROTECTOR.WHITE_LIST:
            pass
        elif hostname in REFER_PROTECTOR.records:
            REFER_PROTECTOR.records.get(hostname)[1] += 1
            if time.time() - REFER_PROTECTOR.records.get(hostname)[0] > REFER_PROTECTOR.TIME_LIMIT * 60:
                REFER_PROTECTOR.records.pop(hostname)
            elif REFER_PROTECTOR.records.get(hostname)[1] > REFER_PROTECTOR.ACCESS_LIMIT:
                REFER_PROTECTOR.records.get(hostname)[0] = time.time()
                return JsonResponse(dict(status=False, data="Too many attempts from your site!"))
            REFER_PROTECTOR.records.get(hostname)[0] = time.time()

        elif hostname in REFER_PROTECTOR.BLACK_LIST:
            return JsonResponse(dict(status=False, data="Your site is in our black list!"))
        else:
            REFER_PROTECTOR.records[hostname] = [time.time(), 1]

        return func(request, *args, **kwargs)
    return decorator


# i, l, 1, 0, o
def passwd_generator(length):
    charset = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 122)) # 0-9, a-z, A-Z
    confused = [48, 49, 73, 76, 79, 105, 108, 111]
    list(map(charset.remove, confused))
    passwd = ''
    for i in range(length):
        passwd += chr(sample(charset, 1)[0])
    return passwd


def save_file(file):
    def tee(func, data):
        func(data)
        return data

    tmp_filename = str(uuid.uuid1())
    while os.path.exists(os.path.join(TMP_PATH, tmp_filename)):
        tmp_filename = str(uuid.uuid1())

    # Hash object
    h_obj = hash_method()

    with open(os.path.join(TMP_PATH, tmp_filename), 'wb') as f:
        list(map(f.write, map(lambda x: tee(h_obj.update, x), file.chunks())))

    hash_value = h_obj.hexdigest()
    fst = hash_value[:2]
    scd = hash_value[2:4]
    path = os.path.join(DATA_PATH, fst, scd)
    if not os.path.exists(path):
        os.makedirs(path)

    # Same hash
    if os.path.exists(os.path.join(path, hash_value)):
        os.remove(os.path.join(TMP_PATH, tmp_filename))
    else:
        os.rename(os.path.join(TMP_PATH, tmp_filename), os.path.join(path, hash_value))

    return hash_value


def verify_recaptcha(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        url = 'https://www.google.com/recaptcha/api/siteverify'
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if not recaptcha_response:
                data = dict(secret=RECAPTCHA_KEY, response=recaptcha_response)
                print(data)
                data = urllib.parse.urlencode(data).encode()
                req = urllib.request.Request(url, data=data)
                response = urllib.request.urlopen(req)
                result = json.loads(response.read().decode())
                print(result.get('success', None))
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
