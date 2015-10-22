# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse


def templates_handler(request, path):
    '''
    功能描述:用于页面的接口将template文件简单渲染
    参数说明:request通过GET或者POST请求带有参数url将会转向地址 url 其中url需要quote编码
    返回说明:HttpResponse对象
    '''
    try:
        #读取模板文件
        template = get_template(path)
        context = RequestContext(request)
        #渲染页面
        html = template.render(context)
        return HttpResponse(html)
    except:
        return HttpResponse('')