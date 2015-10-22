#-*- coding: utf-8 -*-
import time
import md5
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.common.decorators import signature_auth,maintenance_auth,session_auth,platform_auth,needuser
from apps.oclib.utils import rkjson as json
from apps.logics import process_api
from apps.config import reload_all
from apps.common import utils
from apps.config import game_config
from apps.models.config import Config
from apps.models.account_mapping import AccountMapping
from apps.models.random_names import Random_Names

@signature_auth
#@maintenance_auth
#@session_auth
@needuser
def api(request):
    data = {}
    reload_all()
    now = int(time.time())
    data['data'] = {
                    'server_now':now,
                    'cag':utils.create_sig(str(now)),
                    'cog':md5.new(str(now) + 'random_kk').hexdigest()
                    }
    rc,func_data = process_api(request)
    data['data'].update(func_data)
    data['rc'] = rc
    return HttpResponse(
              json.dumps(data, indent=1),
              content_type='application/x-javascript',
        )

def info(request):
    #"""返回当前服务器状态
    #"""
    reload_all()
    data = {        
        'language_version':game_config.system_config.get('language_version', '1.00'),
        'version':game_config.system_config['version'],
        'app_url':game_config.system_config['app_url'],
        'maintenance':game_config.system_config['maintenance'],
        'server_now':int(time.time()),
        'oc_account':game_config.system_config.get('account_assign_switch',False),
        'subareas_conf':eval(Config.get('subareas_conf').data), #分区信息
        'notice':game_config.system_config.get("notice",'')#公告的url
    }
    return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )
    
@signature_auth
#@maintenance_auth
@platform_auth
def index(request):
    #""" 应用首页,输出top page
    #"""
    reload_all()
    data = {
         'rc':0,
         'data':{
            'server_now':int(time.time()),
            'pid':request.oc_user.pid,
            'uid':request.oc_user.uid,
            'newbie':request.oc_user.property_info.newbie,
            'newbie_step':request.oc_user.property_info.newbie_step,
         }
    }
    if request.REQUEST.get('platform') == 'oc':
        data['data']['oc_openid'] = request.oc_user.account.openid
        data['data']['oc_access_token'] = request.oc_user.account.access_token
    
    return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            ) 
    
@signature_auth
# @maintenance_auth            
# @session_auth
@needuser
def select_role(request):
    """新手选择角色，取名字，完成注册
    """    
    data = {}
    username = request.REQUEST.get('name','').strip()
    cid = request.REQUEST.get('cid')
    oc_user = request.oc_user
        
    if not cid:
        data['rc'] = 1
        data['msg'] = u'请输入选择角色'
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',)
    
    if len(username.strip())<=0:
        data['rc'] = 2
        data['msg'] = u'请输入名字'
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',)
    
    if len(username) > 5:
        data['rc'] = 3
        data['msg'] = u'名字长度不能超过5个字符'
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',)
    
    if utils.is_sense_word(username):
        data['rc'] = 4
        data['msg'] = u'名字还有屏蔽字'
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',)  
          
    if oc_user.property_info.property_info["newbie"] is False:
        data['rc'] = 0
        data['msg'] = u''
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',)
        
    if oc_user.set_name(username):
        __remove_random_name(username)
        data['rc'] = 0
        data['msg'] = u''
        #选角色
        from apps.models.user_cards import UserCards
        user_cards_obj = UserCards.get_instance(oc_user.uid)
        if user_cards_obj.cid == "": 
            user_cards_obj.cid = cid
            user_cards_obj.put()

        #更新newbie
        oc_user.property_info.property_info["newbie"] = False
        oc_user.property_info.put()
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',)
    else:
        __remove_random_name(username)
        data = {'rc':5,'msg':'该名字已经存在'}    
        return HttpResponse(json.dumps(data, indent=1), content_type='application/x-javascript',) 

def __remove_random_name(name):
    """删除随机名字
    """
    try:
        random_name_obj = Random_Names.get(name)
        if random_name_obj:
            random_name_obj.delete()
    except:
        utils.debug_print(traceback.format_exc())
        utils.send_exception_mailEx()
        
def language_version(request):
    """返回当前语言包信息
    """    
    data = game_config.language_config
    return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )

def page_not_found(request):
    #"""404 Not Found handler.
    #"""
    
    if request.path == '/api/':
        return HttpResponse(json.dumps({'rc': 0,'ec': 404}),content_type = 'application/json')
    else:
        return render_to_response('404.html',{},context_instance = RequestContext(request))
    
def server_error(request):
    #"""500 Internal Server Error handler.
    #"""
    if request.path == '/api/':
        return HttpResponse(json.dumps({'rc': 0,'ec': 500}),content_type = 'application/json')
    else:
        return render_to_response('500.html',{},context_instance = RequestContext(request))
