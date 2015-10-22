#-*- coding: utf-8 -*-
from apps.oclib import app
from apps.common.utils import send_exception_mail,print_err

class StorageMiddleware(object):
    def process_request(self, request):
        app.pier.clear()
        return None

    def process_response(self, request, response):
        try:
            app.pier.save()
        except:
            print_err()
            send_exception_mail(request)
        return response
