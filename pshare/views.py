from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import MultipleObjectsReturned
from django.utils.encoding import smart_str

from .models import UserFile
from pwShare.settings import DATA_PATH, MAX_FILE_SIZE, SITE_KEY, MAX_PASSWD_GEN_TIME, BASE_DIR, SITE_BASE_URL
from .utils import *

from mimetypes import guess_type
from datetime import datetime

from IPython import embed

import logging
import random
import time
import re
import os


@require_http_methods(['POST', 'GET', ])
@csrf_exempt
@verify_recaptcha
def upload(request):
    if request.method == 'POST':
        if not request.recaptcha_is_valid and False:
            return JsonResponse(dict(status=False, data="Invalid re-captcha token! DO NOT try to scrap my site!"))

        file = request.FILES.get('file')
        alias = request.POST.get('alias', '')
        public = dict(false=False, true=True).get(request.POST.get('public'), False)
        passwd = passwd_generator(4)

        if not file or len(file) > MAX_FILE_SIZE * 1024 * 1024:
            return JsonResponse(dict(status=False, data="Don't you think I'll check your input on server side?"))

        # Check alias
        alias_pattern = re.compile(r'^[^/]{7,32}$')
        if len(alias) > 0:
            if re.match(alias_pattern, alias) is None:
                return JsonResponse(dict(status=False, data="Don't you think I'll check your input on server side?"))

        hash_value = save_file(file)
        check_hash = UserFile.objects.filter(sha1=hash_value)
        if len(check_hash) > 0:
            passwd = check_hash[0].passwd
            if public != check_hash[0].public:
                check_hash[0].public = public
                check_hash[0].save()
        else:
            # Validate passwd
            passwd_list = [_.passwd for _ in UserFile.objects.filter(alias=alias)]
            start = time.time()
            while passwd in passwd_list and time.time() - start < MAX_PASSWD_GEN_TIME:
                if time.time() - start < MAX_PASSWD_GEN_TIME / 2:
                    passwd = passwd_generator(4)
                else:
                    passwd = passwd_generator(6)

            if time.time() - start > MAX_PASSWD_GEN_TIME:
                return JsonResponse(dict(status=False,
                        data="You've chosen a really really popular tag, what a lucky guy~ Please try another tag"))

            user_file = UserFile(
                filename=file.name,
                alias=alias if len(alias) > 0 else '',
                passwd=passwd,
                sha1=hash_value,
                uploaded_date=datetime.utcnow(),
                public=public
            )

            user_file.save()

        res_dict = dict(
            has_alias=len(alias) > 0,
            passwd=passwd,
            long_link=SITE_BASE_URL + hash_value + '/',
            short_link=SITE_BASE_URL + alias + '/',
        )

        res = render(request, 'pshare/show_result.html', res_dict)
        return JsonResponse(dict(status=True, data=smart_str(res.content)))
    else:
        return render(request, 'pshare/index.html', dict(site_key=SITE_KEY))


@require_http_methods(['GET', 'POST', ])
@csrf_exempt
@verify_recaptcha
def download(request, prefix):
    if len(prefix) == 40:
        prefix = prefix.lower()

    if request.method == 'POST':
        if not request.recaptcha_is_valid and False:
            print(request.recaptcha_is_valid)
            return render(request, 'pshare/download.html',
                          dict(is_bot=True, bot_alert=random.choice(bot_alerts), site_key=SITE_KEY, prefix=prefix,
                               prevable=True))
        passwd = request.POST.get('Password')
        is_preview = request.POST.get('Preview')
        is_prevable = True
        if len(prefix) == 40:
            try:
                files = UserFile.objects.filter(sha1=prefix)
                if len(files) == 1 and guess_type(files[0].filename)[0] not in prevable_list:
                    is_prevable = False
                file = get_object_or_404(UserFile, sha1=prefix, passwd=passwd)
                if guess_type(file.filename) in prevable_list:
                    is_prevable = True
            except MultipleObjectsReturned as e:
                file = UserFile.objects.filter(sha1=prefix, passwd=passwd)[0]
            except Http404:
                return render(request, 'pshare/download.html',
                              dict(prefix=prefix, wrong=True, prevable=is_prevable, site_key=SITE_KEY))
        else:
            try:
                files = UserFile.objects.filter(alias=prefix)
                if len(files) == 1 and guess_type(files[0].filename)[0] not in prevable_list:
                    is_prevable = False
                file = get_object_or_404(UserFile, alias=prefix, passwd=passwd)
                if guess_type(file.filename) in prevable_list:
                    is_prevable = True
            except MultipleObjectsReturned as e:
                logging.error(repr(e))
                return HttpResponse(status=500)
            except Http404:
                return render(request, 'pshare/download.html',
                              dict(prefix=prefix, wrong=True, prevable=is_prevable, site_key=SITE_KEY))

        hash_value = file.sha1
        path = os.path.join(DATA_PATH, hash_value[:2], hash_value[2:4], hash_value)
        f = open(path, 'rb')
        chunk = []
        while True:
            data = f.read(4096)
            if not data:
                break
            else:
                chunk.append(data)

        response = StreamingHttpResponse(chunk)

        if is_preview and is_prevable:
            response['Content-Type'] = guess_type(file.filename)[0]
            response['Content-Disposition'] = 'inline; filename="%s"' % file.filename
        else:
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename="%s"' % file.filename
        return response

    else:
        is_file_existed = False
        is_prevable = True
        # SHA-1
        if len(prefix) == 40:
            files = UserFile.objects.filter(sha1=prefix)
            if len(files) > 0:
                is_file_existed = True
        else:
            files = UserFile.objects.filter(alias=prefix)
            if len(files) > 0:
                is_file_existed = True

        if is_file_existed:
            if len(files) == 1 and guess_type(files[0].filename)[0] not in prevable_list:
                is_prevable = False
            return render(request, 'pshare/download.html', dict(prefix=prefix, prevable=is_prevable, site_key=SITE_KEY))
        else:
            raise Http404(repr(prefix) + ' is not found, please check the SHA-1 or alias you inputted.')

# rt_file = open(r'C:\Users\Neil\Desktop\survey.pdf', 'rb')
# response = HttpResponse(content=rt_file, content_type='application/pdf')
# response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('test.pdf')
# response['X-Sendfile'] = smart_str()
