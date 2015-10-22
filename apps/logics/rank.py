#-*- coding: utf-8 -*-
from apps.models.user_base import UserBase
from apps.models.user_cards import UserCards
from apps.models.user_equipments import UserEquipments
from apps.models.compete_rank import get_compete_rank
from apps.models.rank import Rank
from apps.models.guild_user import GuildUser
from apps.models.guild_base import GuildBase
#from apps.models.virtual.card_npc import CardNpc
from apps.models.user_title import UserTitle
from apps.config import game_config

def get_rank_info(oc_user, params):
    '''排行榜首页
    '''
    data = {}
    rank_list = ['force_rank','ca_1_rank','ca_2_rank','ca_3_rank','guild_rank','exp_rank']    
    for obj in rank_list:
        temp = {}
        rank_obj = Rank(oc_user.subarea,obj)
        result = rank_obj.get(1,desc=True)
        if result:
            if obj == "guild_rank":
                gid = result[0][0]
                guild_base_obj = GuildBase.get(gid)
                temp["name"] = guild_base_obj.gname
                temp["lv"] = guild_base_obj.lv 
                user_cards_obj = UserCards.get(guild_base_obj.gleader)
                temp["cid"] = user_cards_obj.cid 
                temp["uid"] = guild_base_obj.gleader
            elif obj == "exp_rank":
                uid = result[0][0]
                user_cards_obj = UserCards.get(uid)
                temp["cid"] = user_cards_obj.cid                        
                temp["force"] = user_cards_obj.force
                temp["username"] = user_cards_obj.user_base.username   
                temp["exp"] = user_cards_obj.user_base.property_info.property_info["exp"]  
                temp["uid"] = uid
            else:
                uid = result[0][0]   
                user_cards_obj = UserCards.get(uid)
                temp["cid"] = user_cards_obj.cid                        
                temp["force"] = user_cards_obj.force
                temp["username"] = user_cards_obj.user_base.username
                temp["uid"] = uid
        data[obj] = temp 
        
    #竞技         
    compete_rank_obj = get_compete_rank(oc_user.subarea)
    ranking_list = compete_rank_obj.get(1,desc=False)
    if ranking_list:
        uid = result[0][0]   
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid                        
        temp["force"] = user_cards_obj.force
        temp["username"] = user_cards_obj.user_base.username
        temp["uid"] = uid
    else:  
        compete_config = game_config.compete_config     
        temp = {}
        npc_lv = int(compete_config["rank_conf"][str(i)]["npc_lv_base"])            
        temp["uid"] = "npc"
        temp["name"] = top_npc_config["name"]
        temp["lv"] = npc_lv
        temp["guild_name"] = ''
        temp["force"] = 1000
    data["compete_rank"] = temp
    return 0,{"result":data}

def force_rank(oc_user, params):
    '''战力榜
    '''
    data = {}
    rank_obj = Rank(oc_user.subarea,'force_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data['ranking_list'] = []
    for obj in ranking_list:    
        uid = obj[0]
        temp = {}
        temp['uid'] = uid
        user_base = UserBase.get(uid)
        temp['name'] = user_base.username
        temp['lv'] = user_base.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid                        
        temp["force"] = user_cards_obj.force
        temp['sign'] = ''
        temp["guild_name"] = ''
        guild_user_obj = GuildUser.get_instance(uid)
        if guild_user_obj.gid:
            guild_base_obj = GuildBase.get_instance(uid)
            temp["guild_name"] = guild_base_obj.gname
        data['ranking_list'].append(temp)
    return 0,data

def ca_1_rank(oc_user, params):
    '''战士战力榜
    '''
    data = {}
    rank_obj = Rank(oc_user.subarea,'ca_1_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data['ranking_list'] = []
    for obj in ranking_list:
        uid = obj[0]
        temp = {}
        temp['uid'] = uid
        user_base = UserBase.get(uid)
        temp['name'] = user_base.username
        temp['lv'] = user_base.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid                        
        temp["force"] = user_cards_obj.force
        temp['sign'] = ''
        temp["guild_name"] = ''
        guild_user_obj = GuildUser.get_instance(uid)
        if guild_user_obj.gid:
            guild_base_obj = GuildBase.get_instance(uid)
            temp["guild_name"] = guild_base_obj.gname
        data['ranking_list'].append(temp)
    return 0,data

def ca_2_rank(oc_user, params):
    '''法师战力榜
    '''
    data = {}
    rank_obj = Rank(oc_user.subarea,'ca_2_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data['ranking_list'] = []
    for obj in ranking_list:
        uid = obj[0]
        temp = {}
        temp['uid'] = uid
        user_base = UserBase.get(uid)
        temp['name'] = user_base.username
        temp['lv'] = user_base.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid                        
        temp["force"] = user_cards_obj.force
        temp['sign'] = ''
        temp["guild_name"] = ''
        guild_user_obj = GuildUser.get_instance(uid)
        if guild_user_obj.gid:
            guild_base_obj = GuildBase.get_instance(uid)
            temp["guild_name"] = guild_base_obj.gname
        data['ranking_list'].append(temp)
    return 0,data

def ca_3_rank(oc_user, params):
    '''猎人战力榜
    '''
    data = {}
    rank_obj = Rank(oc_user.subarea,'ca_3_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data['ranking_list'] = []
    for obj in ranking_list:
        uid = obj[0]
        temp = {}
        temp['uid'] = uid
        user_base = UserBase.get(uid)
        temp['name'] = user_base.username
        temp['lv'] = user_base.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid                        
        temp["force"] = user_cards_obj.force
        temp['sign'] = ''
        temp["guild_name"] = ''
        guild_user_obj = GuildUser.get_instance(uid)
        if guild_user_obj.gid:
            guild_base_obj = GuildBase.get_instance(uid)
            temp["guild_name"] = guild_base_obj.gname
        data['ranking_list'].append(temp)
    return 0,data

def compete_rank(oc_user,params):
    """竞技榜
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
            temp["guild_name"] = ''
            temp["force"] = 1000
            guild_user_obj = GuildUser.get_instance(uid)
            if guild_user_obj.gid:
                guild_base_obj = GuildBase.get_instance(uid)
                temp["guild_name"] = guild_base_obj.gname            
            data['ranking_list'][str(rank)] = temp
    
    #如果前20名中存在npc，则读取npc配置        
    top_npc = game_config.compete_npc_config["top_npc"]
    compete_config = game_config.compete_config     
    for i in range(20):
        i+=1
        if (str(i) not in data["ranking_list"]) and (str(i) in top_npc):
            temp = {}
            npc_lv = int(compete_config["rank_conf"][str(i)]["npc_lv_base"])
            top_npc_config = top_npc[str(i)]
            temp["uid"] = "npc"
            temp["name"] = top_npc_config["name"]
            temp["lv"] = npc_lv
            temp["guild_name"] = ''
            temp["force"] = 1000
            data['ranking_list'][str(i)] = temp            
    return 0,data

def guild_rank(oc_user,params):
    """公会排行帮
    """
    data = {}
    rank_obj = Rank(oc_user.subarea,'guild_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data['ranking_list'] = []
    for obj in ranking_list:
        temp = {}
        gid = obj[0]
        guild_base = GuildBase.get(gid)
        if guild_base is None:
            continue 
        temp = {}
        temp["gname"] = guild_base.gname
        temp["gid"] = guild_base.gid
        temp["gnotice"] = guild_base.gnotice
        temp["exp"] = guild_base.gexp
        temp["lv"] = guild_base.lv
        objGuildUser = GuildUser.get(guild_base.gleader)
        temp["gleader"] = objGuildUser.name
        temp["uid"] = guild_base.gleader
        user_cards_obj = UserCards.get(guild_base.gleader)
        temp["cid"] = user_cards_obj.cid
        data['ranking_list'].append(temp)  
    return 0,data

def exp_rank(oc_user, params):
    '''经验战力榜
    '''
    data = {}
    rank_obj = Rank(oc_user.subarea,'exp_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data['ranking_list'] = []
    for obj in ranking_list:
        uid = obj[0]
        temp = {}
        temp['uid'] = uid
        user_base = UserBase.get(uid)
        temp['name'] = user_base.username
        temp['lv'] = user_base.property_info.property_info["lv"]
        temp['exp'] = user_base.property_info.property_info["exp"]
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid                        
        temp['sign'] = ''
        temp["guild_name"] = ''
        guild_user_obj = GuildUser.get_instance(uid)
        if guild_user_obj.gid:
            guild_base_obj = GuildBase.get_instance(uid)
            temp["guild_name"] = guild_base_obj.gname
        data['ranking_list'].append(temp)
    return 0,data

def get_user_info(oc_user,params):
    """获取人物详细
    """
    data = {}
    uid = params["uid"]
    user_base = UserBase.get(uid)
    data['name'] = user_base.username
    data['lv'] = user_base.property_info.property_info["lv"]
    user_cards_obj = UserCards.get(uid)
    data["cid"] = user_cards_obj.cid
    data["uid"] = uid
    #装备信息
    user_equipments_obj = UserEquipments.get_instance(uid)
    equipments = {}
    for _,v in user_cards_obj.equipments.items():
        if v:
            equipments[v] = user_equipments_obj.equipments[v]            
    data["equipments"] = equipments
    data["user_equipments"] = user_cards_obj.equipments
    #称号
    user_title_obj = UserTitle.get_instance(oc_user.uid)
    data["user_title"] = user_title_obj.title_info["is_used"]
    return 0,{"result":data}