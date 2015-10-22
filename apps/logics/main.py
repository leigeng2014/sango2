#-*- coding: utf-8 -*-
import time
#import datetime
import random

from apps.config import game_config
from apps.models.user_login import UserLogin
from apps.models.user_cards import UserCards
from apps.models.user_teams import UserTeams
from apps.models.user_dungeon import UserDungeon
from apps.models.user_award import UserAward
#from apps.models.user_property import UserProperty
from apps.models.user_equipments import UserEquipments
#from apps.models.user_material import UserMaterial
from apps.models.user_title import UserTitle
from apps.models.random_names import Random_Names

def index(oc_user,params):
    data = {}
    #用户登录信息
    user_login_obj = UserLogin.get_instance(oc_user.uid)
    user_login_obj.login(params)
    data["total_login_num"] = user_login_obj.login_info["total_login_num"]
    data["continuous_login_num"] = user_login_obj.login_info["continuous_login_num"] 
    
    #用户主角信息
    user_card_obj = UserCards.get(oc_user.uid)
    data['leader_info'] = {'cid':user_card_obj.cid,\
                           'skill_offensive':user_card_obj.skill_offensive,\
                           'skill_defensive':user_card_obj.skill_defensive,\
                           'skill_offline':[],
                           'equipments':user_card_obj.equipments,}
    #用户佣兵信息
    user_team_obj = UserTeams.get_instance(oc_user.uid)        
    data['teams_info'] = user_team_obj.teams_info
    data['develop_info'] = user_team_obj.develop_info
    data['team'] = user_team_obj.team  
    
    #用户战场信息
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    data['max_floor_id'] = user_dungeon_obj.dungeon_info.get('max_floor_id',1) 
    data["dun_boss_num"] = user_dungeon_obj.dungeon_info.get("dun_boss_num",3)
    data["buy_dun_boss_num"] = user_dungeon_obj.dungeon_info.get("buy_dun_boss_num",0)
    data["buy_fast_dun_num"] = user_dungeon_obj.dungeon_info.get("buy_fast_dun_num",0)    
    data["fast_dun_num"] = user_dungeon_obj.dungeon_info.get("buy_fast_dun_num",0) #需要弃用的
    data["sweep_boss_num"] = user_dungeon_obj.dungeon_info.get("sweep_boss_num",0)
    data["dun_special_num"] = user_dungeon_obj.dun_special_num
    data["buy_special_dun_num"] = user_dungeon_obj.buy_special_dun_num
    data["max_special_floor_id"] = user_dungeon_obj.max_special_floor_id
    data["max_expedition_floor_id"] = user_dungeon_obj.max_expedition_floor_id
    data["expedition_fail_record"] = {}
    data["expedition_fail_time"] = user_dungeon_obj.expedition_fail_time
    data["expedition_today_record"] = user_dungeon_obj.expedition_today_record
    data["expedition_reset_record"] = user_dungeon_obj.expedition_reset_record
    data["expedition_first_record"] = user_dungeon_obj.expedition_first_record
    
    #我的礼包
    data["my_award"] = {}
    user_award_obj = UserAward.get_instance(oc_user.uid) 
    for award_type in ["login","continuous_login","charge","dungeon","user_lv"]:
        data["my_award"][award_type] = user_award_obj.get_next_award(award_type)["id"]
        
    #我的称号
    data["title"] = {}
    user_title_obj = UserTitle.get_instance(oc_user.uid)
    data["title"]["is_used"] = user_title_obj.title_info["is_used"]
    data["title"]["title_record"] = user_title_obj.title_info["title_record"]
    
    #我的签名
    data["sign"] = oc_user.sign
    data["username_cold_time"] = oc_user.username_cold_time
        
    #挂机设置
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    data["equip_settings"] = user_equipments_obj.equip_settings
    data["chat_server"] = {"host":'42.121.15.153',"port":9906}  
    data["guild_chat_server"] = {"host":'42.121.15.153',"port":9906} 
    return 0,data

def edit_sign(oc_user,params):
    """修改签名
    """
    content = params["content"]
    if len(content) > 20:
        return 1,{"msg":u"签名不能超过20个字符"}    
    oc_user.baseinfo['sign'] = content
    oc_user.put()
    return 0,{}

def edit_username(oc_user,params): 
    """修改昵称
    """
    username = params["username"]
    if len(username) > 5:
        return 1,{"msg":u"签名不能超过5个字符"}
    
    diamond = game_config.system_config.get("edit_username_cost",200)
    username_cold_time = game_config.system_config.get("username_cold_time",7*24*3600)
    if oc_user.username_cold_time and (oc_user.username_cold_time - int(time.time()) < username_cold_time):
        return 2,{"msg":u"冷却时间还没到"} 
        
    if oc_user.property_info.minus_diamond(diamond):
        oc_user.baseinfo['username'] = username
        oc_user.baseinfo['username_cold_time'] = int(time.time())
        oc_user.put()
        return 0,{"username_cold_time":oc_user.baseinfo['username_cold_time']}
    return 3,{"msg":u"你的钻石不够"}

def get_random_names(oc_user,params):
    #"""取得随机名字 返回：random_names:['xxx','yyy']
    #"""
    rand_num = random.random()
    random_list = Random_Names.find({'random' : { '$gte' : rand_num }},limit=20)
    if not random_list:
        random_list = Random_Names.find({'random' : { '$lte' : rand_num }},limit=20)
    data={'random_names':[]}
    if random_list:
        for random_name_obj in random_list:
            data['random_names'].append(random_name_obj.name)
    else:
        data['random_names'] = [u'历史大轮回哦',u'千年等一回哦哦']
    return 0,data    

def receive_award(oc_user,params):
    """领取奖励
    """
    data = {}   
    award = {} 
    award_type = params["type"]
    aid = params["id"]    
    award_config = game_config.award_config
    user_award_obj = UserAward.get_instance(oc_user.uid) 
    next_aid = user_award_obj.get_next_award(award_type)["id"]
    if award_type == "continuous_login":
        now = datetime.datetime.now()
        date = next_aid.keys()[0]
        days = str(next_aid.values()[0])
        if (date != aid) or (date > str(now.date())):
            return 1,{"msg":"this award is not exist"}
                 
        continuous_config = award_config["continuous_login"]
        if days in continuous_config:
            award = continuous_config[str(days)]["rewards"]
        else:
            days = max([int(i) for i in continuous_config.keys()])
            award = continuous_config[str(days)]["rewards"]            
        user_award_obj.continuous_login_award.pop(aid)
    else:
        if aid != next_aid:
            return 2,{"msg":"this award is not exist"}
         
        #开服奖励
        if award_type == "login":
            user_login_obj = UserLogin.get_instance(oc_user.uid)
            total_login_num = user_login_obj.login_info["total_login_num"]
            if total_login_num < int(aid):
                return 3,{"msg":"you can not get this award"}            
            user_award_obj.login_award.append(aid)

        #签到奖励
        if award_type == "sign":
            user_login_obj = UserLogin.get_instance(oc_user.uid)
            total_login_num = user_login_obj.login_info["total_login_num"]
            if total_login_num < int(aid):
                return 4,{"msg":"you can not get this award"}            
            user_award_obj.sign_award.append(aid)

        #充值奖励    
        elif award_type == "charge":
            #判断该奖励是否达到充值奖励对应的奖励
            user_property_obj = UserProperty.get(oc_user.uid)
            charge_sum = user_property_obj.property_info["charge_sum"]
            if (charge_sum * 10) < int(aid):
                return 5,{"msg":"you can not get this award"}
            user_award_obj.charge_award.append(aid)
            
        #战场奖励    
        elif award_type == "dungeon":
            user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
            max_floor_id = user_dungeon_obj.dungeon_info["max_floor_id"]
            if int(aid) > max_floor_id:
                return 6,{"msg":"this award have not arrived"}
            user_award_obj.dungeon_award.append(aid)  
        #等级奖励    
        elif award_type == "user_lv":
            #判断等级是否达到要求
            lv = oc_user.property_info.property_info["lv"]
            if int(aid) > lv:
                return 7,{"msg":"this award have not arrived"} 
            user_award_obj.user_lv_award.append(aid)        
        award = award_config[award_type][aid]["rewards"]
         
    data["result"] = __get_award(oc_user,award)
    user_award_obj.put()
    data["next_award"] = user_award_obj.get_next_award(award_type)
    return 0,data
 
def __get_award(oc_user,award):
    """给奖励
    """
    user_property_obj = UserProperty.get(oc_user.uid)
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    result = {}    
    for _,v in award.items():
        if v["type"] == "coin":
            user_property_obj.add_coin(v["num"])
            result["coin"] = v["num"]  
                       
        elif v["type"] == "diamond":
            user_property_obj.add_diamond(v["num"])
            result["diamond"] = v["num"]
             
        elif v["type"] == "smelting":
            user_property_obj.add_smelting(v)
            result["smelting"] = v["num"]
             
        elif v["type"] == "cp":
            user_property_obj.add_cp(v)
            result["cp"] = v["num"]
             
        elif v["type"] == "equip":
            if len(v["id"]) == 1:
                eid = v["id"][0]
            else:
                user_cards_obj = UserCards.get(oc_user.uid)
                category = user_cards_obj.category
                eid = v["id"][int(category)-1]   
            gemSlot = v.get("gemSlot",0)  #开孔个数           
            eqdbid,equipment = user_equipments_obj.add_equipment(eid,int(v["grade"]),hole=gemSlot)
            if result.get("equipments"):
                result["equipments"].update({eqdbid:equipment})
            else: 
                result["equipments"] = {eqdbid:equipment}    
                             
        elif v["type"] == "item":
            material = user_material_obj.add_material(v["id"],v["num"])
            if result.get("items"):
                result["items"].append(material)
            else:
                result["items"] = [material]
    return result

def get_user_detail_list(oc_user, params):
    """用户详细信息
    """
    result = [] 
    uid_list = params["uid"]  
    uid_list = uid_list.split(',')
    for uid in uid_list:
        temp = {}
        temp['uid'] = uid
        temp['name'] = oc_user.username
        temp['lv'] = oc_user.property_info.property_info["lv"]
        user_cards_obj = UserCards.get(uid)
        temp["cid"] = user_cards_obj.cid
        user_equipments_obj = UserEquipments.get_instance(uid)
        equipments = {}
        for _,v in user_cards_obj.equipments.items():
            if v:
                equipments[v] = user_equipments_obj.equipments[v]
        temp["force"] = user_cards_obj.force
        temp["equipments"] = equipments
        temp["user_equipments"] = user_cards_obj.equipments
        result.append(temp)   
    return 0,{"user_detail_list":result} 
        
def get_config(oc_user, params):    
    config_info = {
        'max_friend_num':game_config.system_config.get("max_friend_num",30), #好友上限        
        'addBossNum_cost':game_config.system_config.get("addBossNum_cost",50),#增加boss挑战次数的消耗配置
        'edit_username_cost':game_config.system_config.get("edit_username_cost",200),#修改昵称消耗
        'username_cold_time':game_config.system_config.get("username_cold_time",7),#修改昵称冷却时间
        
        'compete_cold_time':game_config.compete_config.get("compete_cold_time"), #竞技冷却时间
        'open_compete_force':game_config.compete_config.get("open_compete_force"),   #竞技开放需要的战斗力     
        'contestNum_cost':game_config.compete_config.get("contestNum_cost"),#竞技增加挑战次数消耗配置
        'contestNum':game_config.compete_config.get("contestNum"),           #竞技每日挑战次数

        'team_develop_config':game_config.team_config["team_develop_config"], 
        'team_skill_refresh_config':game_config.team_config["team_skill_refresh_config"],       
        'shuffle_costBase':game_config.equipment_forge_config.get("shuffle_costBase"), #洗练消耗金币初始
        'shuffle_costGrowth':game_config.equipment_forge_config.get("shuffle_costGrowth"), #洗练消耗金币成长
        'coin_shop':game_config.shop_extra_config.get("coin_shop"),
        'refresh_cost':game_config.system_config.get("refresh_cost",20), #打造刷新消耗钻石
        'equipNum_limit':game_config.system_config.get("equipNum_limit",20), #装备背包初始容量上限
        'equipExpand_cost':game_config.system_config.get("equipExpand_cost",20), #装备背包扩充消耗钻石
        'equipExpand_num':game_config.system_config.get("equipExpand_num",20), #装备背包一次扩充格子数
        'equipExpand_limit':game_config.system_config.get("equipExpand_limit",20), #装备背包扩充次数上限
        'addBossNum_cost':game_config.system_config.get("addBossNum_cost",20), #增加boss挑战次数消耗钻石
        'quickPve_limit':game_config.system_config.get("quickPve_limit",20), #每日可快速战斗次数
        'quickPve_cost':game_config.system_config.get("quickPve_cost",20), #快速战斗消耗钻石
        #'open_compete_force':1000,#开放竞技需要的战力
        'horn_config':{"1":10,"2":20,'3':50},#喇叭需要的砖石
    }       
    return 0, config_info

def get_card_config(oc_user, params):
    """获得卡的配置
    """
    return 0, {'card_conf':game_config.card_config}

def get_card_category_config(oc_user, params):
    """获得角色类型的配置
    """
    return 0, {'card_category_config':game_config.card_category_config}

def get_card_level_config(oc_user, params):
    """获得卡等级的配置
    """
    return 0, {'card_level_config':game_config.card_level_config}

def get_dungeon_config(oc_user,params):
    """取得目前的战场配置
    """
    return 0, {'dungeon_config':game_config.dungeon_config}

def get_special_dungeon_config(oc_user,params):
    """取得精英战场配置
    """
    return 0, {'special_dungeon_config':game_config.special_dungeon_config}

def get_monster_config(oc_user,params):
    """取敌将配置
    """
    return 0, {'monster_conf':game_config.monster_config}    

def get_shop(oc_user,params):
    """商店配置信息：{   'com.oneclick.sango.coin01':1,#状态：0-default;1-热销;2-超值}        
    """
    result = {}
    for sale_k,sale_v in game_config.shop_config['sale'].iteritems():
        result[sale_k] = sale_v.get('state',0)
    return 0,{'shop_info':result}

def get_shop_extra_config(oc_user,params):
    """商店设定配置       
    """
    return 0,{'shop_extra_config':game_config.shop_extra_config}

def get_skill_config(oc_user,params):
    """获得武将的技能配置
    """
    return 0, {'skill_config':game_config.skill_config} 

def get_material_config(oc_user,params):
    """获得道具配置
    """
    return 0, {'material_config':game_config.material_config} 

def get_equipment_config(oc_user,params):
    """获得装备配置
    """
    return 0, {'equipment_config':game_config.equipment_config} 

def get_equipment_drop_config(oc_user,params):
    """获得装备掉落配置
    """
    return 0, {'drop_config':game_config.equipment_drop_config["drop_config"]} 

def get_equipment_strengthen_config(oc_user,params):
    """装备强化配置
    """
    return 0, {'equipment_strengthen_config':game_config.equipment_strengthen_config}

def get_equip_config(oc_user,params):
    """获得装备配置
    """
    return 0, {'equipment_config':game_config.equipment_config} 

def get_equip_drop_config(oc_user,params):
    """获得装备掉落配置
    """
    return 0, {'drop_config':game_config.equipment_drop_config["drop_config"]} 

def get_equip_strengthen_config(oc_user,params):
    """装备强化配置
    """
    return 0, {'equipment_strengthen_config':game_config.equipment_strengthen_config}

def get_special_attr_config(oc_user,params):
    """装备强化配置
    """
    return 0, {'special_attr_config':game_config.special_attr_config}

def get_gem_config(oc_user,params):
    """宝石配置
    """
    return 0, {'gem_config':game_config.gem_config}

def get_award_config(oc_user,params):
    """礼包配置
    """
    return 0, {'award_config':game_config.award_config}

def get_vip_config(oc_user,params):
    """vip配置
    """
    return 0,{"vip_config":game_config.vip_config}
    
def get_guild_config(oc_user,params):
    """guild配置
    """
    return 0,{"guild_config":game_config.guild_config}

def get_expedition_dungeon_config(oc_user,params):
    """远征战场配置
    """
    return 0,{"expedition_dungeon_config":game_config.expedition_dungeon_config}

def get_title_config(oc_user,params):
    """称号配置
    """
    return 0,{"title_config":game_config.title_config}
