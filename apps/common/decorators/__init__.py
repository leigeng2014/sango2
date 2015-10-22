#-*- coding: utf-8 -*-
import time
from django.http import HttpResponse

from apps.oclib import app
from apps.oclib.utils import rkjson as json

from apps.common import utils
from apps.config import game_config
from apps.models.user_base import UserBase
from apps.models.account_mapping import AccountMapping
from apps.models.session import Session

def platform_auth(func):
    """ 接口加上这个修饰将进行平台验证
    """
    def new_func(request,*args,**argw):
        # 用户在首次登陆时或再次登陆访问时（大多数情况下是访问/路径时）
        # 需要与开放平台进行验证，主要验证access_token以及openid
        access_token = request.REQUEST.get('access_token','')
        openid = request.REQUEST.get('openid','')
        platform = request.REQUEST.get('platform','')
        if platform == 'oc':
            result,pid,msg = auth_token_for_oc(request,access_token,openid)
            if not result:
                data = {'rc':100,'data':{'msg':msg,'server_now':int(time.time())}}
                return HttpResponse(
                    json.dumps(data, indent=1),
                    content_type='application/x-javascript',
                )
        else:
            result = False
            
        if not result:
            data = {'rc':101,'data':{'msg':utils.get_msg('login','platform_overdue'),'server_now':int(time.time())}}
            return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )
        #验证成功
        else:
            #写入session    
            Session.set(platform, pid)
        result = func(request,*args,**argw)
        return result
    return new_func

def session_auth(func):
    """ 接口加上这个修饰将进行session验证
    """
    def new_func(request,*args,**argw):
        #此装饰器用于对api的请求，验证session
        para_pid = request.REQUEST.get('pid',None)
        para_platform = request.REQUEST.get('platform',None)

        session_overdue = False
        if para_platform is None or para_pid is None:
            session_overdue = True
        platform,pid = Session.get(para_platform+':'+para_pid)
        if not platform or not pid or platform != para_platform or para_pid != pid:
            session_overdue = True

        #session过期
        if session_overdue:
            data = {'rc':103,'data':{'msg':utils.get_msg('login','server_exception'),'server_now':int(time.time())}}
            return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )
        result = func(request,*args,**argw)
        return result
    return new_func

def signature_auth(func):
    """ 接口加上这个修饰将进行session验证
    """
    def new_func(request,*args,**argw):
        #此装饰器用于对api的请求，验证客户端签名
        try:
            #认证通过
            result = func(request,*args,**argw)
            return result
        except:
            utils.print_err()
            #清空storage
            app.pier.clear()
            #send mail
            utils.send_exception_mail(request)
            data = {'rc':107,'data':{'msg':utils.get_msg('login','server_exception'),'server_now':int(time.time())}}
            return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )
    return new_func

def maintenance_auth(func):
    """ 接口加上这个修饰将进行游戏维护验证
    """
    def new_func(request,*args,**argw):
        try:
            subarea = request.REQUEST.get('subarea', '1')
            if game_config.system_config['maintenance']:
                pid = request.REQUEST.get('pid','')
                platform = request.REQUEST.get('platform','')
                openid = request.REQUEST.get('openid','')                
                allow = False
#                 if platform and (pid or openid):
#                     uid = __get_uid(platform, openid, pid, subarea)
#                     if uid and uid in game_config.system_config.get('allow_uids',[]):
#                         allow = True
                if not allow:
                    data = {'rc':108,'data':{'msg':get_msg('login','maintenance'),'server_now':int(time.time())}}
                    return HttpResponse(
                        json.dumps(data, indent=1),
                        content_type='application/x-javascript',
                    )
            result = func(request,*args,**argw)
            return result
        except:
            utils.print_err()
            app.pier.clear()
            send_exception_mail(request)
            data = {'rc':109,'data':{'msg':get_msg('login','server_exception'),'server_now':int(time.time())}}
            return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )
    return new_func

def needuser(func):
    """ 接口加上这个修饰将安装用户，需要先验证"""
    def new_func(request,*args,**argw):
        pid = request.REQUEST.get("pid")
        platform = request.REQUEST.get("platform")
        subarea = request.REQUEST.get("subarea", "1")
        if pid and platform:
            #调用UserBase的install方法安装用户
            request.oc_user = UserBase._install(pid, platform, subarea=subarea)
        else:
            data = {'rc':111,'data':{'msg':utils.get_msg('login','platform_overdue'),'server_now':int(time.time())}}
            return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )
        return func(request,*args,**argw)
    return new_func

def auth_token_for_oc(request,access_token,openid):
    """论证无账号用户
    """    
    pid = ''    
    msg = ''
    fg = False    
    subarea = request.REQUEST.get("subarea", "1")
    #没有openid时，检查后控制自动分配id的开头是否开启，如果已经关闭，返回提示
    if not openid:
        if game_config.system_config.get('account_assign_switch'):
            fg = True
            pid = utils.get_uuid()
            #验证成功，安装用户
            request.oc_user = UserBase._install(pid,'oc',subarea)
            access_token = utils.get_upwd()
            request.oc_user.account.update_info(pid, access_token)
        else:
            msg = utils.get_msg('login','cannot_register')
        return fg,pid,msg
    
    if not utils.check_openid(openid):
        msg = utils.get_msg('login','cannot_register')
        return fg,pid,msg
    
    #有openid时，检查access_token是否正确
    account = AccountMapping.get(openid)
    if account and account.access_token == access_token:
        fg = True
        pid = openid
        request.oc_user = UserBase._install(pid,'oc',subarea)
        #验证成功，安装用户
    else:
        msg = utils.get_msg('login','session_overdue')
    return fg,pid,msg