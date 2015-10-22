#-*- coding: utf-8 -*-
import copy
import datetime
from apps.common import utils
from apps.config import game_config

from apps.models.user_mail import UserMail
from apps.models.user_cards import UserCards
from apps.models.user_compete import UserCompete
from apps.models.virtual.card_npc import CardNpc
from apps.models.user_property import UserProperty
from apps.models.compete_rank import get_compete_rank
from apps.models.user_equipments import UserEquipments
from apps.models.user_compete_record import UserCompeteRecord
from apps.models.user_compete_message import UserCompeteMessage
from apps.models.user_base import UserBase
from apps.models.guild_user import GuildUser
from apps.models.guild_base import GuildBase

def get_compete_info(oc_user,params):
    """获取用户的竞技首页
    """
    data = {}
    user_compete_obj = UserCompete.get_instance(oc_user.uid)
    data["my_rank"] = user_compete_obj.my_rank
    data["my_reward"] = user_compete_obj.get_my_reward
    data["compete_num"] = user_compete_obj.compete_info.get("compete_num",0)
    data["buy_num"] = user_compete_obj.compete_info.setdefault("buy_num",0)
    data['last_fail_time'] = user_compete_obj.last_fail_time
    return 0,data

def get_my_enemy(oc_user,params):
    """获取我的竞技对手
    """
    data = {}
    user_compete_obj = UserCompete.get_instance(oc_user.uid)
    data["compete_list"] = user_compete_obj.get_my_enemy()
    return 0,data

def get_rank_info(oc_user,params):
    """获取前20名的排行
    """
    data = {}
    compete_rank_obj = get_compete_rank(oc_user.subarea)
    ranking_list = compete_rank_obj.get(20,desc=False)
    data['ranking_list'] = {}
    #先查看真实用户的前20名的排名
    for uid,rank in ranking_list:
        rank = int(rank)
        if rank <= 20:
            temp = {}
            temp['uid'] = uid
            user_base = UserBase.get(uid)
            temp['name'] = user_base.username
            temp['lv'] = user_base.property_info.property_info["lv"]
            user_cards_obj = UserCards.get(uid)
            temp["cid"] = user_cards_obj.cid
            temp["force"] = user_cards_obj.force 
            temp["sign"] = user_base.sign
            temp["guild_name"] = ''
            guild_user_obj = GuildUser.get_instance(uid)
            if guild_user_obj.gid:
                guild_base_obj = GuildBase.get_instance(uid)
                temp["guild_name"] = guild_base_obj.gname
            data['ranking_list'][str(int(rank))] = temp 
    
    #如果前20名中存在npc，则读取npc配置        
    top_npc = game_config.compete_npc_config["top_npc"]
    compete_config = game_config.compete_config     
    for i in range(20):
        i+=1
        if (str(i) not in data["ranking_list"]) and (str(i) in top_npc):
            temp = {}
            npc_lv = int(compete_config["rank_conf"][str(i)]["npc_lv_base"])
            top_npc_config = top_npc[str(i)]
            temp["force"] = 1000
            temp["sign"] = u''
            temp["uid"] = "npc"
            temp["cid"] = top_npc_config["icon"]
            temp["name"] = top_npc_config["name"]
            temp["lv"] = npc_lv
            temp["guild_name"] = ''
            data['ranking_list'][str(i)] = temp
    return 0,data

def compete_record(oc_user,params):
    """竞技记录
    """
    user_compete_obj = UserCompete.get_instance(oc_user.uid)
    user_compete_obj.send_rank_reward()
    data = {}
    data["result"] = {}
    compete_record_obj = UserCompeteRecord.hgetall(oc_user.uid)
    if not compete_record_obj:
        return 0,data    
    n = 0
    result = {}
    for k,v in compete_record_obj.items():
        n+=1 
        compete_uid = v["record_info"]["compete_uid"]
        if compete_uid != "npc":
            try:
                temp = {}
                #获取用户的个人信息
                user_equipments_obj = UserEquipments.get_instance(compete_uid)
                user_cards_obj = UserCards.get(compete_uid)
                equipments = {}
                for _,v_ in user_cards_obj.equipments.items():
                    if v_:
                        equipments[v_] = user_equipments_obj.equipments[v_]
                user_card_dict = user_cards_obj.card_obj().__dict__                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                user_card_dict.pop('card_category_config')
                user_card_dict.pop('card_detail')
                temp.update({'user_equipmenmts':user_cards_obj.equipments,'equipments':equipments})
                temp.update(user_card_dict)
                result[k] = {"user_info":temp,"record_info":v["record_info"]}
            except:
                pass
        #大于100的删除    
        if n > 20:
            compete_record = UserCompeteRecord.hget(oc_user.uid,k)
            compete_record.delete()     
    data["result"] = result
    return 0,data

def compete_message(oc_user,params):
    """我的留言
    """
    data = {}
    compete_message_obj = UserCompeteMessage.hgetall(oc_user.uid)
    message = copy.deepcopy(compete_message_obj)
    data["result"] = {}    
    if not message:        
        return 0,data
    n = 0
    for m in message:
        if m != '' and m != "npc":
            message[m].pop("uid")
            message[m].pop("ouid")       
            user_cards_obj = UserCards.get(m) 
            cid = user_cards_obj.cid
            name = user_cards_obj.user_base.baseinfo["username"]
            message[m].update({"datetime":message[m]["record_info"][-1]["create_time"],"cid":cid,"name":name})
                #大于100的删除 
        n += 1    
        if n > 20:
            compete_message = UserCompeteMessage.hget(oc_user.uid,m)
            compete_message.delete()  
    data["result"] = message
    return 0,data

def send_message(oc_user,params):
    """留言
    """
    to_uid = params.get("to_uid")
    content = params.get("content",'')
    if not to_uid:
        return 1,{"msg":"please choose user"}
    
    if not content:
        return 2,{"msg":"please input content"}
    
    if len(content) > 40:
        return 3,{"msg":"content too long"}
    
    compete_message_obj = UserCompeteMessage.hget(oc_user.uid,to_uid)
    compete_message_obj.set_message(oc_user.uid,to_uid,content)
    
    compete_message_obj = UserCompeteMessage.hget(to_uid,oc_user.uid)
    compete_message_obj.set_message(oc_user.uid,to_uid,content)
    return 0,{}

def delete_message(oc_user,params):
    """删除留言,to_uid 为''时，删除全部记录
    """
    to_uid = params.get("to_uid",'')
    if to_uid != '':
        compete_message_obj = UserCompeteMessage.hget(oc_user.uid,to_uid)
        compete_message_obj.delete()
    else:
        all_message = UserCompeteMessage.hgetall(oc_user.uid)
        for k,_ in all_message.items():
            obj = UserCompeteMessage.hget(oc_user.uid,k)
            obj.delete()
    return 0,{}     

def extand_num(oc_user,params):
    """增加我的竞技次数
    """
    diamond = 0
    cost_config = game_config.compete_config.get("contestNum_cost",{"1":20})    
    user_compete_obj = UserCompete.get_instance(oc_user.uid)
    buy_num = int(user_compete_obj.compete_info["buy_num"])
    if str(buy_num + 1) in cost_config:
        diamond = cost_config[str(buy_num + 1)] 
    else:
        diamond = max(cost_config.values())
         
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.minus_diamond(diamond):        
        user_compete_obj.compete_info["compete_num"] += 1
        user_compete_obj.compete_info["buy_num"] += 1
        user_compete_obj.put()
        return 0,{"compete_num":user_compete_obj.compete_info["compete_num"]}
    return 1,{'msg':'not enough diamond'}

def end(oc_user,params):
    """结算竞技
    """
    data = {}
    enemy_uid = params.get("uid","npc")
    enemy_name = params.get("name","")
    enemy_rank = int(params.get("rank",9999))
    result = int(params.get("result",0))
    user_compete_obj = UserCompete.get_instance(oc_user.uid)
    #先判断免费次数是否充足
    if user_compete_obj.compete_info["compete_num"] <= 0:
        return 1,{'msg':u'您的挑战次数为不足'} 
    
    if user_compete_obj.last_fail_time and (int(time.time()) - user_compete_obj.last_fail_time < 5*60):
        return 2,{"msg":u"您的冷却时间还没到"}
        
    #判断对手的排名是否比自己高
    my_rank = user_compete_obj.my_rank
    if my_rank <= enemy_rank:
        return 3,{"msg":u"不能打比自己排名低的玩家"}

    #战斗
    if result:        
        compete_rank_obj = get_compete_rank(oc_user.subarea)
        #交换排名，并且记录信息
        if enemy_uid == "npc":
            if compete_rank_obj.get_name_by_score(enemy_rank,enemy_rank):
                return 4,{"msg":u"对手排名已经改变"}
            compete_rank_obj.set(oc_user.uid,enemy_rank)
        else:
            if int(compete_rank_obj.score(enemy_uid)) != int(enemy_rank):
                return 5,{"msg":u"对手排名已经改变"}
            compete_rank_obj.set(oc_user.uid,enemy_rank) 
            compete_rank_obj.set(enemy_uid,my_rank)
        #添加竞技记录，双方都要记录    
        sid = utils.create_gen_id()
        compete_record_obj = UserCompeteRecord.hget(oc_user.uid,sid)
        compete_record_obj.set_record(enemy_uid,enemy_name,1,1,my_rank,enemy_rank)
        if enemy_uid != "npc":            
            #记录对手的挑战信息
            enemy_compete_record_obj = UserCompeteRecord.hget(enemy_uid,sid)
            enemy_compete_record_obj.set_record(oc_user.uid,oc_user.baseinfo["username"],2,0,enemy_rank,my_rank)
            #给对手发邮件
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content = u"%s，您在竞技中被 [%s] 打败，排名从 %s 下滑到 %s。" % (now,oc_user.baseinfo["username"],enemy_rank,my_rank)
            user_mail = UserMail.hget(enemy_uid,sid)
            user_mail.set_mail(mtype="compete",content = content,awards={})
            
        #称号     
        from apps.models.user_title import UserTitle
        user_title_obj = UserTitle.get_instance(oc_user.uid)
        user_title_obj.set_title('2')
        user_title_obj.set_title('4') 
        #清空失败时间
        if user_compete_obj.compete_info["last_fail_time"]:
            user_compete_obj.compete_info["last_fail_time"] = ''       
    else:
        sid = utils.create_gen_id()
        #添加竞技记录，失败只记录我自己的
        compete_record_obj = UserCompeteRecord.hget(oc_user.uid,sid)
        compete_record_obj.set_record(enemy_uid,enemy_name,1,0,my_rank,my_rank)
        user_compete_obj.compete_info["last_fail_time"] = int(time.time()) 
    data["last_fail_time"] = user_compete_obj.compete_info["last_fail_time"]
    data["mtype"] = "compete"
    user_compete_obj.compete_info["compete_num"] -= 1
    user_compete_obj.put()  
    return 0,data

# def __get_compete_obj(uid,user_rank):
#     """获得竞技对象
#     """
#     data = {}    
#     if uid == "npc":
#         rank_conf = copy.deepcopy(game_config.compete_config["rank_conf"])
#         rank_conf_sort = sorted(rank_conf.items(),key=lambda x:int(x[0]))
#         reward_rank = 1
#         if str(user_rank) in rank_conf:
#             reward_rank = user_rank
#         else:
#             for ran in rank_conf_sort:
#                 reward_rank = int(ran[0])
#                 if int(ran[0]) > user_rank:                 
#                     break                                        
#         npc_id = rank_conf[str(reward_rank)]["npcId"]
#         npc_lv_base = rank_conf[str(reward_rank)]["npc_lv_base"]
#         npc_lv_growth = rank_conf[str(reward_rank)]["npc_lv_growth"]
#         npc_lv =  int(npc_lv_base + (reward_rank - user_rank)*npc_lv_growth)        
#         compete_npc_config = game_config.compete_npc_config
#         if user_rank > 20:
#             npc_name = utils.random_choice(compete_npc_config["common_npcName"],1)[0]
#             npc_icon = utils.random_choice(compete_npc_config["common_npcIcon"],1)[0]
#             common_npc_config = compete_npc_config["common_npc"]                    
#             npc_config = common_npc_config[npc_id]
#             npc_card_obj = CardNpc.get(npc_icon,npc_lv,npc_config)  
#             
#             data.update({"rank":user_rank,"uid":"npc","cid":npc_icon,"name":npc_name}) 
#             npc_card_dict = copy.deepcopy(npc_card_obj.__dict__)
#             npc_card_dict.pop("card_detail")
#             npc_card_dict.pop("card_category_config")
#             npc_card_dict.pop("subarea")
#             data.update(npc_card_dict)
#         else:
#             top_npc_config = compete_npc_config["top_npc"][npc_id]
#             npc_card_obj = CardNpc.get(top_npc_config["icon"],npc_lv,top_npc_config)
#             data.update({"rank":user_rank,"uid":"npc","cid":top_npc_config["icon"],"name":top_npc_config["name"]}) 
#             npc_card_dict = copy.deepcopy(npc_card_obj.__dict__)
#             npc_card_dict.pop("card_detail")
#             npc_card_dict.pop("card_category_config")
#             npc_card_dict.pop("subarea")
#             data.update(npc_card_dict)
#     else:
#         uid = uid
#         user_cards_obj = UserCards.get(uid)
#         user_equipments_obj = UserEquipments.get_instance(uid)
#         equipments = {}
#         for _,v in user_cards_obj.equipments.items():
#             if v:
#                 equipments[v] = user_equipments_obj.equipments[v]
#         user_base_obj  = user_cards_obj.user_base
#         lv = user_base_obj.property_info.property_info["lv"]
#         cid = user_cards_obj.cid
#         user_card_dict = user_cards_obj.card_obj().__dict__
#         data.update(user_card_dict)
#         name = user_base_obj.baseinfo["username"]  
#         data.update({"rank":user_rank,"uid":uid,"lv":lv,"cid":cid,"name":name,\
#                      'user_equipmenmts':user_cards_obj.equipments,'equipments':equipments})
#     return data