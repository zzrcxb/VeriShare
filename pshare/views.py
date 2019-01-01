from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import MultipleObjectsReturned
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper

from .models import UserFile
from pwShare.settings import DATA_PATH, MAX_FILE_SIZE, SITE_KEY, BASE_DIR, SITE_BASE_URL
from .utils import *
from .settings import MAX_PASSWD_GEN_TIME

from mimetypes import guess_type
from datetime import datetime

import logging
import random
import time
import re
import os


@require_http_methods(['POST', 'GET', ])
@csrf_exempt
@verify_recaptcha
def upload(request):
    def store_userfile():
        UserFile(
            filename=file.name,
            alias=alias if len(alias) > 0 else '',
            passwd=passwd,
            sha1=hash_value,
            uploaded_date=datetime.utcnow(),
            public=public
        ).save()

    def revoke():
        dup_file = dup_files[0]
        dup_file.filename = file.name
        dup_file.passwd = passwd
        dup_file.uploaded_date = datetime.utcnow()
        dup_file.save()
        if not public:
            res_dict['revoked'] = True

    def revoke_pub(file):
        file.delete()
        res_dict['revoked_pub'] = True

    if request.method == 'POST':
        if not request.recaptcha_is_valid:
            return JsonResponse(dict(status=False, data="Invalid re-captcha token! DO NOT try to scrap my site!"))

        file = request.FILES.get('file')
        alias = request.POST.get('alias', '')
        public = dict(false=False, true=True).get(request.POST.get('public'), False)
        passwd = passwd_generator(4)

        if not file or len(file) > MAX_FILE_SIZE * 1024 * 1024:
            return JsonResponse(dict(status=False, data="Don't you think I'll check your input on server side?"))

        # Check alias
        alias_pattern = re.compile(r'^[\w\d_-]{7,32}$')
        if len(alias) > 0:
            if re.match(alias_pattern, alias) is None:
                return JsonResponse(dict(status=False, data="Don't you think I'll check your input on server side?"))

        hash_value = save_file(file)

        # Generate passwd
        if not public:
            check_hash = UserFile.objects.filter(sha1=hash_value)
            check_alias = UserFile.objects.filter(alias=alias) if len(alias) > 0 else []
            passwd_list = [_.passwd for _ in check_hash] + [_.passwd for _ in check_alias]
            start = time.time()
            while passwd in passwd_list and time.time() - start < MAX_PASSWD_GEN_TIME:
                if time.time() - start < MAX_PASSWD_GEN_TIME / 2:
                    passwd = passwd_generator(4)
                else:
                    passwd = passwd_generator(6)

            if time.time() - start > MAX_PASSWD_GEN_TIME:
                return JsonResponse(dict(status=False,
                                         data="You've chosen a really really popular tag, what a lucky guy~ Please try another tag"))
        else:
            passwd = ''

        res_dict = dict(
            has_alias=len(alias) > 0,
            public=public,
            passwd=passwd,
            long_link=SITE_BASE_URL + hash_value + '/',
            short_link=SITE_BASE_URL + alias + '/',
            revoked=False,
            revoked_pub=False
        )

        dup_files = UserFile.objects.filter(sha1=hash_value, alias=alias, public=public)
        dup_pub_files = UserFile.objects.filter(sha1=hash_value, public=True)

        if len(UserFile.objects.filter(sha1=hash_value)) > 0:
            if not public and len(dup_pub_files) > 0:
                revoke_pub(dup_pub_files[0])

            if len(dup_files) > 0:
                revoke()
            else:
                store_userfile()
        else:
            store_userfile()

        res = render(request, 'pshare/show_result.html', res_dict)
        return JsonResponse(dict(status=True, data=smart_str(res.content)))
    else:
        return render(request, 'pshare/index.html', dict(site_key=SITE_KEY))


@require_http_methods(['GET', ])
def download_page(request, prefix):
    if len(prefix) == 40:
        prefix = prefix.lower()

    is_prevable = True

    # SHA-1
    if len(prefix) == 40:
        files = UserFile.objects.filter(sha1=prefix)
        if len(files) > 0:
            filename = files[0].filename
        else:
            raise Http404
        for file in files:
            if file.public == True:
                return redirect('/%s/download/' % prefix) # Direct download public files
    else:
        files = UserFile.objects.filter(alias=prefix)
        if len(files) > 0:
            filename = prefix
        else:
            raise Http404

    filenames = list({_.filename for _ in files})
    if len(filenames) == 1 and guess_type(filenames[0])[0] not in prevable_list:
        is_prevable = False

    return render(request, 'pshare/download.html',
                  dict(prefix=prefix, filename=filename, prevable=repr(is_prevable), site_key=SITE_KEY))


@require_http_methods(['POST', 'GET'])
@refer_limitation
@csrf_exempt
@verify_recaptcha
def download(request, prefix, method):
    if len(prefix) == 40:
        prefix = prefix.lower()

    if request.method == 'POST':
        if not request.recaptcha_is_valid:
            return HttpResponse("Invalid re-captcha token! DO NOT try to scrap my site!")

        passwd = request.POST.get('passwd')
        enquiry_params = dict()
        if len(prefix) == 40:
            enquiry_params['sha1'] = prefix
        else:
            enquiry_params['alias'] = prefix

        files = UserFile.objects.filter(**enquiry_params)
        if len(files) == 0:
            raise Http404
        else:
            filenames = list({_.filename for _ in files})
            is_prevable = True
            if len(filenames) == 1 and guess_type(filenames[0])[0] not in prevable_list:
                is_prevable = False

            file = None
            for _ in files:
                if _.passwd == passwd:
                    file = _
                    break
            if not file:
                return render(request, 'pshare/download.html',
                              dict(wrong_passwd="True", prefix=prefix,
                                   filename=file.name if len(prefix) == 40 else prefix, prevable=repr(is_prevable),
                                   site_key=SITE_KEY))
    else:
        enquiry_params = dict()
        if len(prefix) == 40:
            enquiry_params['sha1'] = prefix
            if prefix in ['cdf141de37a5c7a798770248ac03bc1333bd06fa', 'c00cc97fddb383afa60bcede918921d4d5d88949']:
                print('===========Cong!==========\n\n\n' + prefix + "\n\n\n===========================")
        else:
            return redirect('/%s/' % prefix)

        files = UserFile.objects.filter(**enquiry_params)
        if len(files) == 0:
            raise Http404
        print(any({_.public for _ in files}))
        if not any({_.public for _ in files}):
            return redirect('/%s/' % prefix)

    response = return_file(files[0], guess=method == 'preview', stream=method == 'preview')
    print("return preview file")
    return response


def return_file(file, guess=False, stream=False):
    hash_value = file.sha1
    if stream:
        path = os.path.join(DATA_PATH, hash_value[:2], hash_value[2:4], hash_value)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(path, 'rb'), chunk_size))
        response['Content-Length'] = os.path.getsize(path)
    else:
        path = os.path.join('/data/', hash_value[:2], hash_value[2:4], hash_value)
        response = HttpResponse()
        response['X-Accel-Redirect'] = path

    if guess:
        response['Content-Disposition'] = 'inline; filename="%s"' % file.filename
        response['Content-Type'] = guess_type(file.filename)[0]
        print(guess_type(file.filename)[0])
    else:
        response['Content-Disposition'] = 'attachment; filename="%s"' % file.filename
        response['Content-Type'] = 'application/octet-stream'
    return response
