#-*- coding: utf-8 -*-
import time
import datetime
from apps.common import utils
from apps.config import game_config

from apps.models.user_dungeon import UserDungeon
from apps.models.user_cards import UserCards
from apps.models.user_property import UserProperty
from apps.models.user_equipments import UserEquipments
from apps.models.user_material import UserMaterial

# def start(oc_user,params):
#     """战斗
#     """
#     data = {}
#     floor_id = params.get("floor_id",'1')
#     mtype = params.get("mtype","common")
#     #获取我方英雄
#     user_cards_obj = UserCards.get(oc_user.uid)
#     heros_list = [user_cards_obj.card_obj()]
#     
#     #获取敌方英雄
#     conf = game_config.dungeon_config[floor_id]['rooms'][mtype]
#     min_monster = int(conf.get('min_monster',1))
#     max_monster = int(conf.get('max_monster',1))
#     monster_num = random.randint(min_monster,max_monster)
#     monster_list = utils.random_choice(conf['monster'],monster_num)
#     from apps.models.virtual.monster import Monster
#     monster_list = [ Monster.get(mid) for mid in monster_list]
#     
#     #实例化战斗场景
#     from apps.models.virtual.dungeon import Dungeon
#     dun = Dungeon(oc_user.uid)
#     dun.load_first_army(heros_list)
#     dun.load_second_army(monster_list)
#     dun.run()
#     data['result'] = dun.result
#     return 0, data

def end(oc_user,params):
    """战斗
    """
    data = {} 
    floor_id = int(params.get('floor_id',1))#战场id
    mtype = params.get('mtype','common')   #boss/common
    result = int(params.get('result',1))       
    round_num = int(params.get('round_num',1))
    monster = params.get('monster','101101_monster') 
    monster_list = monster.split(',')
    monster_num = len(monster_list)
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    max_floor_id = user_dungeon_obj.dungeon_info["max_floor_id"]
    if floor_id > max_floor_id:
        return 1,{'msg':u"此战场还没有达到"}
    
    if mtype == 'boss' and user_dungeon_obj.dungeon_info.get("dun_boss_num",3) <= 0:
        return 2,{'msg':u"您今天已经用完了boss挑战"}
    
    data['get_award'] = {'total_exp':0,
                         'total_coin':0,
                         'items':{},
                         'equipments':{},
                         }

    dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"][mtype]
    if result == 1:    
        ######加经验和金钱
        total_exp = 100
        total_coin = 100 
        monster_config = game_config.monster_config
        for mid in monster_list:
            total_exp += monster_config[mid]["drop_exp"]
            total_coin += monster_config[mid]["drop_coin"]
        user_property_obj = UserProperty.get(oc_user.uid)
        user_property_obj.add_exp(total_exp)
        user_property_obj.add_coin(total_coin)
        data['get_award']['total_exp'] = total_exp
        data['get_award']['total_coin'] = total_coin
                                              
        #####加装备新手引导送装备
        if user_dungeon_obj.tutorial_dun_num == 0:
            user_cards_obj = UserCards.get(oc_user.uid)
            category = user_cards_obj.category
            equip_list = ['eq_01001','eq_01002','eq_01003']
            user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
            eqdbid,equipments = user_equipments_obj.add_equipment(equip_list[int(category)-1],1)
            data['get_award']['equipments'][eqdbid] = equipments
        else:
            equip_reward = dungeon_config["reward"]["equip"]
            if equip_reward:
                drop_rate = equip_reward.get("drop_rate",0)
                if utils.is_happen(drop_rate * 1):
                    #根据权重算出掉落的drop_eid,drop_quality
                    drop_quality = utils.get_item_by_random_simple([(k,v) for k,v in equip_reward["drop_quality"].items()])
                    drop_eid = utils.random_choice(equip_reward["drop_list"],1)[0]                
                    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
                    eqdbid,equipments = user_equipments_obj.add_equipment(drop_eid,int(drop_quality))
                    data['get_award']['equipments'][eqdbid] = equipments
                
        #加道具
        all_items = {}
        item_reward = dungeon_config["reward"]["item"]
        if item_reward:            
            drop_rate = item_reward.get("drop_rate",0)
            if utils.is_happen(drop_rate * 1):
                item_drop_list = item_reward["drop_list"]
                weight_id = utils.get_item_by_random_simple([(k,v["weight"]) for k,v in item_drop_list.items()])
                drop_item = item_drop_list[weight_id]["item"]
                drop_num = item_drop_list[weight_id]["num"] 
                all_items[drop_item] = drop_num
                
        #vip用户挑战boss会有额外的道具奖励        
        if mtype == "boss":
            vip_config = game_config.vip_config[user_property_obj.vip_lv]
            boss_dropExtra = vip_config["boss_dropExtra"]
            if boss_dropExtra:                
                if utils.is_happen(boss_dropExtra["drop_rate"]):
                    if boss_dropExtra["id"] in all_items:
                        all_items[boss_dropExtra["id"]] += boss_dropExtra["num"]
                    else:
                        all_items[boss_dropExtra["id"]] = boss_dropExtra["num"]
                        
        if all_items:
            user_material_obj = UserMaterial.get_instance(oc_user.uid)
            for item_id,item_num in all_items.items():
                material = user_material_obj.add_material(item_id, item_num)
                if item_id in data["get_award"]["items"]:
                    data["get_award"]['items'][item_id]["num"] += item_num
                else:
                    data["get_award"]['items'].update(material)
                
    #根据结果更新战场信息    
    user_dungeon_obj.update_dungeon(floor_id,result,mtype,round_num,monster_num) 
    ######战场统计
    data["success_rate"] = int(user_dungeon_obj.success_rate * 100)
    data["average_dungeon_date"] = user_dungeon_obj.average_dungeon_date
    data["average_dungeon_num"] = user_dungeon_obj.average_dungeon_num
    data["equip_drop_rate"] = int(user_dungeon_obj.equip_drop_rate * 100)
    data["average_coin"] = user_dungeon_obj.average_coin
    data["average_exp"] = user_dungeon_obj.average_exp
    data["dun_boss_num"] = user_dungeon_obj.dungeon_info.get("dun_boss_num",5)
    data["buy_boss_num"] = user_dungeon_obj.dungeon_info.get("buy_boss_num",0)
    data["fast_dun_num"] = user_dungeon_obj.dungeon_info.setdefault("fast_dun_num",1)
    print 'success_rate',data["success_rate"]
    print 'average_dungeon_date',data["average_dungeon_date"]
    print 'average_dungeon_num',data["average_dungeon_num"]
    print 'equip_drop_rate',data["equip_drop_rate"]
    print 'average_coin',data["average_coin"]
    print 'average_exp',data["average_exp"]
    return 0, data

def expedition_end(oc_user,params):
    """远征关卡战斗
    """
    data = {}     
    floor_id = params.get('floor_id',1)#战场id
    result = int(params.get("result",0))    
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    if int(floor_id) > int(user_dungeon_obj.max_expedition_floor_id) + 1:
        return 1,{'msg':u"此战场还没有达到"}  
    
    if floor_id in user_dungeon_obj.expedition_today_record:
        return 2,{'msg':u"今天已经打过改战场了"} 
                  
    data["mtype"] = "expedition" 
    data['get_award'] = {
                         'total_exp':0,
                         'total_coin':0,
                         }     
    if result == 1: 
        #战斗胜利给奖励   
        expedition_dungeon_config = game_config.expedition_dungeon_config[str(floor_id)]["drop_list"] 
        for _,v in expedition_dungeon_config.items():
            if v["type"] == "item":
                user_material_obj = UserMaterial.get_instance(oc_user.uid)
                material = user_material_obj.add_material(v["id"], v["num"])
                if 'items' not in data["get_award"]:
                    data["get_award"]["items"] = {}
                data["get_award"]['items'].update(material)
            elif v["type"] == "popularity":
                data["get_award"]['popularity'] = v["num"]
                
        if int(floor_id) != user_dungeon_obj.max_expedition_floor_id:
            #根据结果更新战场信息    
            user_dungeon_obj.dungeon_info["max_expedition_floor_id"] = int(floor_id)
        user_dungeon_obj.dungeon_info["expedition_today_record"].append(floor_id)
        #记录首杀
        if floor_id not in user_dungeon_obj.expedition_first_record:
            user_dungeon_obj.expedition_first_record[floor_id] = oc_user.username  
        #称号     
        from apps.models.user_title import UserTitle
        user_title_obj = UserTitle.get_instance(oc_user.uid)
        user_title_obj.set_title('1')
            
    elif result == 0:
        user_dungeon_obj.dungeon_info["expedition_fail_time"] = int(time.time())
    
    user_dungeon_obj.put()
    return 0, data

def expedition_sweep(oc_user,params):
    """远征一键扫荡
    """
    data = [] 
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid) 
    max_expedition_floor_id = user_dungeon_obj.dungeon_info["max_expedition_floor_id"]
    expedition_today_record = user_dungeon_obj.expedition_today_record 
    expedition_dungeon_config = game_config.expedition_dungeon_config
    vip_lv = oc_user.property_info.vip_lv
    
    diamond = 20  #每个关卡消费20钻石
    sweep_num = 0 #本次扫荡的关卡数
    no_sweep_dungeon = []#本次扫荡的关卡
    for i in range(int(max_expedition_floor_id)):
        if str(i+1) not in expedition_today_record:
            sweep_num += 1  
            no_sweep_dungeon.append(str(i+1))
                        
    #如果sweep_num 为0 代表没有需要扫荡的关卡                  
    if sweep_num == 0:
        return 1,{"msg":u'您今天已经扫荡过了'}  
      
    #vip_lv 为0 是，消费钻石扫荡
    if vip_lv == 0:
        if not oc_user.property_info.minus_diamond(diamond * sweep_num):
            return 2,{"msg":u"您的钻石不够"}
        
    #给奖励 
    for floor_id in no_sweep_dungeon:
        user_dungeon_obj.dungeon_info["expedition_today_record"].append(floor_id)
        drop_list = expedition_dungeon_config[floor_id]["drop_list"]
        temp = {}
        temp["get_award"] = {"items":{},"popularity":0,"floor_id":floor_id} 
        for _,v in drop_list.items():
            if v["type"] == "item":
                user_material_obj = UserMaterial.get_instance(oc_user.uid)
                material = user_material_obj.add_material(v["id"], v["num"])
                mid = material.keys()[0]
                if mid not in temp["get_award"]["items"]:
                    temp["get_award"]['items'].update(material)
                else:
                    temp["get_award"]['items'][mid]["num"] += v["num"] 
                      
            elif v["type"] == "popularity":
                temp["get_award"]["popularity"] += v["num"]
                oc_user.property_info.add_popularity(v["num"])
        data.append(temp)
            
    user_dungeon_obj.put()     
    return 0, {"result":data}

def expedition_reset(oc_user,params):
    """远征重置
    """
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    today_date = str(datetime.datetime.now().date())
    if today_date in user_dungeon_obj.expedition_reset_record:
        return 1,{"msg":u"您今天已经重置过了"}
    
    #vip_lv 为0 是，消费钻石扫荡
    vip_lv = oc_user.property_info.vip_lv     
    if vip_lv <= 5:
        return 2,{"msg":u"您的vip等级还没达到5级"}
    
    user_dungeon_obj.dungeon_info["expedition_today_record"] = []
    user_dungeon_obj.dungeon_info["expedition_reset_record"].append(today_date)
    user_dungeon_obj.put()     
    return 0, {}

def expedition_remove_fail(oc_user,params):
    """远征消除冷却
    """
    data = {} 
    diamond = 40
    if not oc_user.property_info.minus_diamond(diamond):
        return 1,{"msg":u"您的钻石不够"}
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    user_dungeon_obj.dungeon_info["expedition_fail_time"] = ''
    user_dungeon_obj.put()     
    return 0, data    

def fast_start(oc_user,params):
    """快速战斗
    """
    data = {}    
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    cost = game_config.system_config.get("quickPve_cost",50)
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.property_info["diamond"] < cost:
        return 1,{"msg":"your diamond is not enough"} 
    
    vip_config = game_config.vip_config[user_property_obj.vip_lv]
    quickPve_num = vip_config["quickPve_num"]
    if int(quickPve_num) <= user_dungeon_obj.dungeon_info["buy_fast_dun_num"]:
        return 2,{"msg":"您购买次数已经用完了"}
    #消耗钻石
    user_property_obj.minus_diamond(cost)
    
    #增加购买快速战斗次数    
    user_dungeon_obj.dungeon_info["buy_fast_dun_num"] += 1   #购买boss的次数
    user_dungeon_obj.put()
    
    data["result"] = user_dungeon_obj.offline_dungeon(dtype="fast")
    return 0,data

def offline_dungeon(oc_user,params): 
    """离线战斗
    """
    data ={}
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    data["result"] = user_dungeon_obj.offline_dungeon()
    return 0,data

def sweep_boss(oc_user,params):
    """扫荡boss
    """
    data = {} 
    floor_id = int(params.get('floor_id',1))#战场id
    mtype = 'boss'   #boss/common
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    max_floor_id = user_dungeon_obj.dungeon_info["max_floor_id"]
    if floor_id > max_floor_id:
        return 1,{'msg':u"此战场还没有达到"}

    if user_dungeon_obj.dungeon_info.get("dun_boss_num",3) <= 0:
        return 2,{'msg':u"您今天已经用完了boss挑战"}
    
    data['get_award'] = {'total_exp':0,
                         'total_coin':0,
                         'items':{},
                         'equipments':{},
                         'box':{},
                         }
    ######加经验和金钱
    dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"][mtype]
    monster_config = game_config.monster_config

    mid = dungeon_config["monster"][0]
    total_exp = monster_config[mid].get("drop_exp",0)
    total_coin = monster_config[mid].get("drop_coin",0)
        
    user_property_obj = UserProperty.get(oc_user.uid)
    user_property_obj.add_exp(total_exp)
    user_property_obj.add_coin(total_coin)
    data['get_award']['total_exp'] = total_exp
    data['get_award']['total_coin'] = total_coin
    
    #加装备
    equip_reward = dungeon_config["reward"]["equip"]
    drop_quality = utils.get_item_by_random_simple([(k,v) for k,v in equip_reward["drop_quality"].items()])
    if equip_reward:
        drop_rate = equip_reward.get("drop_rate",0)
        if utils.is_happen(drop_rate):
            #根据权重算出掉落的drop_eid,drop_quality
            drop_quality = utils.get_item_by_random_simple([(k,v) for k,v in equip_reward["drop_quality"].items()])
            drop_eid = utils.random_choice(equip_reward["drop_list"],1)[0]  
            user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
            eqdbid,equipments = user_equipments_obj.add_equipment(drop_eid,int(drop_quality))
            data['get_award']['equipments'][eqdbid] = equipments            
    #加道具
    all_items = {}
    item_reward = dungeon_config["reward"]["item"]
    if item_reward:            
        drop_rate = item_reward.get("drop_rate",0)
        if utils.is_happen(drop_rate):
            item_drop_list = item_reward["drop_list"]
            weight_id = utils.get_item_by_random_simple([(k,v["weight"]) for k,v in item_drop_list.items()])
            drop_item = item_drop_list[weight_id]["item"]
            drop_num = item_drop_list[weight_id]["num"] 
            all_items[drop_item] = drop_num            
    #vip用户挑战boss会有额外的道具奖励        
    if mtype == "boss":
        vip_config = game_config.vip_config[user_property_obj.vip_lv]
        boss_dropExtra = vip_config["boss_dropExtra"]
        if boss_dropExtra:                
            if utils.is_happen(boss_dropExtra["drop_rate"]):
                if boss_dropExtra["id"] in all_items:
                    all_items[boss_dropExtra["id"]] += boss_dropExtra["num"]
                else:
                    all_items[boss_dropExtra["id"]] = boss_dropExtra["num"]
    if all_items:
        for item_id,item_num in all_items.items():
            data["get_award"].update(__add_item(oc_user,item_id,item_num))
                
    #根据结果更新战场信息    
    user_dungeon_obj.dungeon_info["dun_boss_num"] -= 1
    user_dungeon_obj.put()   
    
    ######战场统计
    return 0, data

def extend_num(oc_user,params):
    """购买boss挑战次数
    """
    data = {}
    user_dungeon_obj = UserDungeon.get_instance(oc_user.uid)
    cost = game_config.system_config.get("addBossNum_cost",50)
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.property_info["diamond"] < cost:
        return 1,{"msg":"your diamond is not enough"} 
    
    vip_config = game_config.vip_config[user_property_obj.vip_lv]
    addBossNum_num = vip_config["addBossNum_num"]
    if addBossNum_num <= user_dungeon_obj.dungeon_info["buy_dun_boss_num"]:
        return 2,{"msg":"您购买次数已经用完了"}
    
    #消耗钻石
    user_property_obj.minus_diamond(cost)    
    #增加购买挑战boss次数    
    user_dungeon_obj.dungeon_info["buy_dun_boss_num"] += 1   #购买boss的次数
    user_dungeon_obj.dungeon_info["dun_boss_num"] += 1       #今天可以打boss的次数
    user_dungeon_obj.put()
    return 0,data

def change_skill(oc_user,params):
    """选择技能,参数skill_list = 'sk_01,sk_02',
       skill_type = skill_offensive/skill_defensive/skill_offline
    """
    skill_list = params['skill_list']
    skill_type = params["skill_type"]
    skill_list = skill_list.split(',')
    user_cards_obj = UserCards.get(oc_user.uid)
    if skill_type == "skill_offensive":
        user_cards_obj.skill_offensive = skill_list
    if skill_type == "skill_defensive":
        user_cards_obj.skill_defensive = skill_list
    user_cards_obj.put()
    return 0,{}  

def horn_chat(oc_user,params):
    """喇叭聊天 消耗砖石
    """
    htype = params.get("type",'1')
    horn_config = {"1":10,"2":20,'3':50}; 
    cost = horn_config[htype]
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.property_info["diamond"] < cost:
        return 1,{"msg":"your diamond is not enough"}
    #消耗钻石
    user_property_obj.minus_diamond(cost)
    return 0,{}
    
