#-*- coding: utf-8 -*-
import datetime
from apps.common import utils
#from apps.models.user_property import UserProperty
from apps.models.user_base import UserBase
from apps.models.user_friend import UserFriend
from apps.models.user_cards import UserCards
from apps.models.level_user import LevelUser
from apps.models.user_equipments import UserEquipments
from apps.config import game_config

def add_request(oc_user,params):
    """添加好友的请求
    """
    fid = params.get('fid','')
    #检查好友id是否存在
    friend = UserBase.get(fid)
    if not friend:
        return 1,{'msg':utils.get_msg('user','no_user')}
    
    #好友不能是自己
    if oc_user.uid == fid:
        return 2,utils.get_msg('friend','cannot_self')    
    
    friend_friend_obj = UserFriend.get_instance(fid)
    #检查自己是否已经申请过
    if oc_user.uid in friend_friend_obj.requests.keys():
        return 3,{'msg':utils.get_msg('friend','no_request')}
    
    user_friend_obj = UserFriend.get_instance(oc_user.uid) 
    #已经添加过的好友不能再添加
    if fid in user_friend_obj.friends.keys():
        return 4,{'msg':utils.get_msg('friend','already_friend')}
    
    max_friend_num = game_config.system_config.get("max_friend_num",30)  
    max_request_num = game_config.system_config.get("max_request_num",30)   
    #检查自己是否已经达到最大好友数量
    if user_friend_obj.friend_num >= max_friend_num:
        return 5,{'msg':utils.get_msg('friend','self_max_friend')}
    
    #检查对方是否已经达到最大好友数量    
    if friend_friend_obj.friend_num >= max_friend_num:
        return 6,{'msg':utils.get_msg('friend','other_max_friend')}
    
    #检查对方的好友请求是否已经达到最大
    if len(friend_friend_obj.requests) >= max_request_num:
        return 7,{'msg':utils.get_msg('friend','self_max_friend')}

    friend_friend_obj.add_request(oc_user.uid)
    return 0,{}

def accept_request(oc_user,params):
    """同意好友申请
    """
    fid = params['fid']
    user_friend_obj = UserFriend.get(oc_user.uid)
    #检查是否有这条请求
    if not fid in user_friend_obj.requests:
        return 1,{'msg':utils.get_msg('friend','no_request')}    
    
    user_friend_obj = UserFriend.get_instance(oc_user.uid)
    #已经添加过的好友不能再添加
    if fid in user_friend_obj.friends:
        return 2,{'msg':utils.get_msg('friend','already_friend')}
    
    #检查自己是否已经达到最大好友数量
    max_friend_num = game_config.system_config["max_friend_num"]
    if user_friend_obj.friend_num >= max_friend_num:
        return 3,{'msg':utils.get_msg('friend','self_max_friend')}
    
    #检查对方是否已经达到最大好友数量
    friend_friend_obj = UserFriend.get_instance(fid)
    if friend_friend_obj.friend_num >= max_friend_num:
        return 4,{'msg':utils.get_msg('friend','other_max_friend')}
    
    #将对方加入到自己的好友列表
    user_friend_obj.add_friend(fid)
    #将自己加入到对方的好友列表
    friend_friend_obj.add_friend(oc_user.uid)
    #将对方从自己的申请列表中删除
    user_friend_obj.del_request(fid)
    return 0,{}

def refuse_request(oc_user,params):
    """拒绝好友申请
    """
    fid = params['fid']
    user_friend_obj = UserFriend.get_instance(oc_user.uid)
    if fid in user_friend_obj.requests:
        user_friend_obj.requests.pop(fid)
        user_friend_obj.put()
    return 0,{}

def del_friend(oc_user,params):
    """删除好友
    """
    fid = params['fid']
    user_friend_obj = UserFriend.get(oc_user.uid)    
    user_friend_obj.del_friend(fid)
    UserFriend.get(fid).del_friend(oc_user.uid)
    return 0,{}

def get_friend_list(oc_user,params):
    """获取好友列表
    """
    data = {'friends':[]}
    user_friend_obj = UserFriend.get_instance(oc_user.uid)
    for fid in user_friend_obj.friends.keys():
        friend_user = UserBase.get(fid)    
        if not friend_user:
            continue 
        temp = {}
        temp['uid'] = fid
        temp['name'] = friend_user.username
        temp['lv'] = friend_user.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(fid)
        temp["cid"] = user_cards_obj.cid
        user_equipments_obj = UserEquipments.get_instance(fid)
        equipments = {}
        for _,v in user_cards_obj.equipments.items():
            if v:
                equipments[v] = user_equipments_obj.equipments[v]                
        temp["force"] = user_cards_obj.force
        temp["equipments"] = equipments
        temp["user_equipments"] = user_cards_obj.equipments   
        data['friends'].append(temp)
    #我的信息    
#     user_info = {}
#     user_info["uid"] = oc_user.uid
#     user_info["name"] = oc_user.username
#     user_info['lv'] = oc_user.property_info.property_info["lv"]
#     user_cards_obj = UserCards.get(oc_user.uid)
#     user_info['cid'] = user_cards_obj.cid
#     user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
#     equipments = {}
#     for _,v in user_cards_obj.equipments.items():
#         if v:
#             equipments[v] = user_equipments_obj.equipments[v]
#     user_info["force"] = user_cards_obj.force
#     user_info["equipments"] = equipments
#     user_info["user_equipments"] = user_cards_obj.equipments 
    data['now_num'] = len(data['friends'])
    data['max_num'] = 40
    return 0,data

def search_friend(oc_user,params):
    """查找好友
    """
    data = {}
    fid = params['fid']
    friend_user = UserBase.get(fid)
    if not friend_user:
        return 1,{'msg':utils.get_msg('user','no_user')}
    
    data['uid'] = fid
    data['name'] = friend_user.username
    data['lv'] = friend_user.property_info.property_info["lv"]
    user_cards_obj = UserCards.get(fid)
    data["cid"] = user_cards_obj.cid
    user_equipments_obj = UserEquipments.get_instance(fid)
    equipments = {}
    for _,v in user_cards_obj.equipments.items():
        if v:
            equipments[v] = user_equipments_obj.equipments[v]
            
    data["force"] = user_cards_obj.force
    data["equipments"] = equipments
    data["user_equipments"] = user_cards_obj.equipments    
    return 0,data

def select_friend(oc_user,params):
    """按照区域选好友
    """
    data = {"friend":[]}
    level_user_obj = LevelUser.get_instance(oc_user.subarea)
    select_friend_list = utils.random_choice(level_user_obj.users,6)
    for fid in select_friend_list:
        friend_user = UserBase.get(fid)    
        if not friend_user:
            continue 
        if fid == oc_user.uid:
            continue
        try:
            temp = {}    
            temp['uid'] = fid
            temp['name'] = friend_user.username
            temp['lv'] = friend_user.property_info.property_info["lv"]
            user_cards_obj = UserCards.get(fid)
            temp["cid"] = user_cards_obj.cid
            user_equipments_obj = UserEquipments.get_instance(fid)
            equipments = {}
            for _,v in user_cards_obj.equipments.items():
                if v:
                    equipments[v] = user_equipments_obj.equipments[v]
                    
            temp["force"] = user_cards_obj.force
            temp["equipments"] = equipments
            temp["user_equipments"] = user_cards_obj.equipments    
            data["friend"].append(temp)
        except:
            pass
    return 0,data
    
def get_request_list(oc_user,params):
    """获取申请列表
    """
    data = {'requests':[]}
    user_friend_obj = UserFriend.get_instance(oc_user.uid)
    for fid in user_friend_obj.requests.keys():
        #大于三天的删除掉
        add_time = utils.timestamp_toDatetime(user_friend_obj.requests[fid]).date()        
        if add_time + datetime.timedelta(days=3) < datetime.datetime.now().date():
            user_friend_obj.requests.pop(fid)
            user_friend_obj.put()
            continue
        
        #用户不存在的排除掉
        friend_user = UserBase.get(fid)
        if not friend_user:
            continue
        
        temp = {}
        temp['uid'] = fid
        temp['name'] = friend_user.username
        temp['lv'] = friend_user.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(fid)
        temp["cid"] = user_cards_obj.cid
        user_equipments_obj = UserEquipments.get_instance(fid)
        equipments = {}
        for _,v in user_cards_obj.equipments.items():
            if v:
                equipments[v] = user_equipments_obj.equipments[v]
                
        temp["force"] = user_cards_obj.force
        temp["equipments"] = equipments
        temp["user_equipments"] = user_cards_obj.equipments 
        data['requests'].append(temp)
    return 0,data
    
def __remove_null(_list):
    """去空
    """
    return [ i for i in _list if i ]