#-*- coding: utf-8 -*-
from apps.models.user_title import UserTitle

def use_title(oc_user,params):
    """设置称号
    """
    tid = params["tid"]
    user_title_obj = UserTitle.get_instance(oc_user.uid)
    if tid == '':
        user_title_obj.title_info['is_used'] = ''
        user_title_obj.put()
        return 0,{}
    else:
        if user_title_obj.use_title(tid):
            return 0,{}
        return 1,{"msg":u"你还没有获取该称号"}
    

