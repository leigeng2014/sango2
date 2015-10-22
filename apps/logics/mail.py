#-*- coding: utf-8 -*-
import datetime
from apps.common import utils
from apps.models.user_mail import UserMail
from apps.models.user_equipments import UserEquipments
from apps.models.user_material import UserMaterial
from apps.models.user_property import UserProperty
from apps.models.user_base import UserBase

def get_all(oc_user,params):
    """获取所有的邮件
    """
    data = {}
    user_mail_obj = UserMail.hgetall(oc_user.uid) 
    result = {}
    now = datetime.datetime.now()
    for k,v in user_mail_obj.items():
        create_time = datetime.datetime.strptime(v["mail_info"]["create_time"],'%Y-%m-%d %H:%M:%S')
        if (now - create_time).days >= 7:
            user_mail_obj = UserMail.hget(oc_user.uid,k)
            user_mail_obj.delete()
            continue
            
        result[k] = {"from_uid":v["mail_info"].get("from_uid","system"),\
                     "from_name":'system',\
                     "type":v["mail_info"]["type"],\
                     "content":v["mail_info"]["content"],\
                     "create_time":v["mail_info"]["create_time"],\
                     "rewards":v["mail_info"]["awards"]}
        #如果是聊天获取from_name
        if v["mail_info"].get("type") == "chat":
            user_base_obj = UserBase.get(v["mail_info"]["from_uid"])
            result[k]["from_name"] = user_base_obj.username
            result[k]["from_uid"] = v["mail_info"]["from_uid"] 
    ###########测试数据############  
#     result = {
#         '1': {"from_uid":'system',\
#              "from_name":'system',\
#              "type":"common",
#              "content":u'你好',
#              "create_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#              "rewards":{},
#          }, 
#         '2': {"from_uid":'system',\
#              "from_name":'system',\
#              "type":"compete",
#              "content":u'你在竞技场中被xxx打败！',
#              "create_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#              "rewards":{}
#          }, 
#         '3': {"from_uid":'system',\
#              "from_name":'system',\
#              "type":"award",
#              "content":u'你在竞技场中被xxx打败！',
#              "create_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#              "rewards":{            
#                 '1':{
#                    'type':'diamond', #物品类型
#                    'num':300, #数量
#                 },
#                 '2':{
#                     'type':'coin', #物品类型
#                     'num':50000, #数量
#                 },
#                 '3':{
#                     'type':'cp', #物品类型
#                     'num':50000, #数量
#                 },
#                 '4':{
#                     'id':'it_05101',  
#                     'num':1,
#                     'type':'item',
#                 },
#                 '5':{
#                     'gemSlot':0,
#                     'grade':'5',
#                     'id':'eq_01001',
#                     'num':1,
#                     'type':'equip',
#                 },
#                 '6':{
#                     'type':'smelting',
#                     'num':500,
#                 },  
#                 '7':{
#                     'type':'popularity',
#                     'num':500,
#                 }                                    
#              },
#         },
#         '4': {"from_uid":'111037',\
#              "from_name":'xxxx',\
#              "type":"chat",
#              "content":u'你好啊！',
#              "create_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#              "rewards":{}
#          }, 
#     } 
    #########################             
    data["mails"] = result 
    return 0, data

def receive(oc_user, params):
    """邮件领奖
    """
    data = {}
    mid = params["mid"]
    user_mail_obj = UserMail.hget(oc_user.uid,mid)
    if not user_mail_obj.mail_info:
        return 1,{"msg":"this mail is not exist"}
    
    awards_info = user_mail_obj.mail_info["awards"]
    user_property_obj = UserProperty.get(oc_user.uid)
    user_equipments_obj = UserEquipments.get(oc_user.uid)
    user_material_obj = UserMaterial.get(oc_user.uid)
    result = {}    
    for _,v in awards_info.items():
        #加金币
        if v["type"] == "coin":
            user_property_obj.add_coin(v["num"])
            result["coin"] = v["num"]  
        #加钻石              
        elif v["type"] == "diamond":
            user_property_obj.add_diamond(v["num"])
            result["diamond"] = v["num"] 
        #加熔炼值    
        elif v["type"] == "smelting":
            user_property_obj.add_smelting(v["num"])
            result["smelting"] = v["num"]
        #加荣誉    
        elif v["type"] == "cp":
            user_property_obj.add_cp(v["num"])
            result["cp"] = v["num"]
        #加装备    
        elif v["type"] == "equip":
            gemSlot = v.get("gemSlot",0)  #开孔个数 
            eqdbid,equipment = user_equipments_obj.add_equipment(v["id"],int(v["grade"]),hole=gemSlot,add_type="email")
            if result.get("equipments"):
                result["equipments"].update({eqdbid:equipment})
            else:
                result["equipments"] = {eqdbid:equipment}
        #加道具        
        elif v["type"] == "item":
            material = user_material_obj.add_material(v["id"],v["num"])
            if result.get("items"):
                result["items"].append(material)
            else:
                result["items"]= [material]
        #加贡献                        
        elif v["type"] == "gcontribution":
            user_property_obj.give_award({"gcontribution":v["num"]})
                
    data["result"] = result
    user_mail_obj.delete()
    return 0,data

def delete(oc_user, params):
    """删除邮件
    """
    mid = params["mid"]
    user_mail_obj = UserMail.hget(oc_user.uid,mid)
    user_mail_obj.delete()
    return 0,{}

def send_mail(oc_user, params):
    """发邮件
    """
    uid = params["uid"]
    content = params["content"]
    sid = utils.create_gen_id()
    user_mail = UserMail.hget(uid,sid)
    user_mail.set_mail(from_uid=oc_user.uid,mtype="chat",content = content)
    return 0,{}