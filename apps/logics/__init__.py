#-*- coding: utf-8 -*-

import datetime
from apps.oclib import app
from apps.config import game_config
from apps.common import utils


def process_api(request):
    """ 
    功能描述:分发处理请求
    参数说明:HttpRequest
    返回说明:dict
    """
    data = {}    
    oc_user = request.oc_user
    params = request.REQUEST
    print 'params=======',params
    method = params.get('method','')
    if not method:
        return 201,{'msg':''}
    sig = params.get('sig','')
    if not sig:
        return 202, {'msg':utils.get_msg('login','refresh')}
    print '%s %s active uid:' % (str(datetime.datetime.now()),method),oc_user.uid

    #版本是否已更新
    if not request.REQUEST.get('version') or (float(request.REQUEST['version']) \
    < float(game_config.system_config.get('version','1.00')) and method != 'dungeon.end'):
        return 203,{'msg':utils.get_msg('login','new_version')}    

    bl_model_str,bl_func_str = method.split('.')[0],method.split('.')[1]
    bl_obj = __import__(bl_model_str,globals(),locals())
    bl_func = getattr(bl_obj, bl_func_str)
    rc,func_data = bl_func(oc_user,params)
    if rc != 0:
        #rc异常时,清空storage
        app.pier.clear()

    data.update(func_data)
    data['user_info'] = oc_user.wrapper_info()
    return rc,data
