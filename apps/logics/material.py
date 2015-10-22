#-*- coding: utf-8 -*-
import random
import copy

from apps.common import utils
from apps.config import game_config
from apps.models.user_material import UserMaterial
from apps.models.user_property import UserProperty
from apps.models.user_dungeon import UserDungeon

def getall(oc_user,params):
    """获取所有材料
    """
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    return 0, {"msg": user_material_obj.materials}

def use(oc_user,params):
    """道具的使用
    """
    mid = params['mid'] 
    material_config = game_config.material_config
    if mid not in material_config:
        return 1,{"msg":u"没有此道具"}
    
    mtype = int(material_config[mid]["type"])
    result = 0,{}
    #宝石强化   宝石
    if mtype == 1:
        result = __gem_upgrade(oc_user,params,material_config)
        
    #开箱子     宝石袋，箱子
    elif mtype == 2:
        result = __open_bag(oc_user,params,material_config)
        
    #消耗了产生别的东西  boss挑战券
    elif mtype == 5:
        result = __boss(oc_user,params) 
    
    elif mtype == 7:
        result = __open_dungeon_box(oc_user,params)
        
    elif mtype == 8:
        result = __special_equip_compose(oc_user,params)
        
    return result

def __gem_upgrade(oc_user,params,material_config):
    """宝石升级
    """
    mid = params['mid']
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    material = user_material_obj.materials.get(mid)
    if not material:
        return 2,{"msg":u"您还没有获得该道具"}   

    exp = material['exp']
    material_config = material_config[mid]
    lv = material_config["lv"]
    target = material_config.get("target",'')
    if not target:
        return 3,{"msg":u"已经达到最大等级"}

    upgrade_cost = material_config["upgrade_cost"]
    coin = upgrade_cost['coin']
    property_obj = UserProperty.get(oc_user.uid)
    
    if not property_obj.minus_coin(coin):
        return 4, {"msg":u"钱不够,需要%s" % coin}
    #宝石
    if "item" in upgrade_cost:
        item = upgrade_cost['item']
        if len(item) != 0:
            for x in item:
                tof = user_material_obj.minus_material(x[0], int(x[1]))
                if not tof:
                    return 5, {"msg":u"材料不够"}  

    gem_config = game_config.gem_config
    upgrade_success = gem_config['gem_upgrade'][str(lv)]["upgrade_success"]
    max_exp = upgrade_success["success_pt"]
    exp_growth = upgrade_success["success_growth"]
    success_rate = upgrade_success["success_rate"]
    success_rate_growth = upgrade_success["success_rate_growth"]
    
    #根据强化次数算出成功率
    num = int(exp / exp_growth) + 1#强化次数
    rate = success_rate +(num - 1)*success_rate_growth 
    flag = False
    if utils.is_happen(rate):
        flag = True
    else:
        exp += exp_growth
        if exp >= max_exp:
            flag = True
            material["exp"] = 0
        else:
            material["exp"] = exp
            result = {mid: material}
        user_material_obj.put()
        
    if flag:
        result = user_material_obj.add_material(target,1)
        user_material_obj.minus_material(mid,1)
    return 0, {"msg":result}

def __open_bag(oc_user,params,material_config):
    """开袋子
    """
    mid = params['mid']
    num = int(params['num'])
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    material = user_material_obj.materials.get(mid)
    if not material:
        return 2,{"msg":"您还没有获得该道具"}
    
    if int(material["num"]) < num:
        return 3,{"msg":"您的道具不足"}
    
    #添加奖励
    reward = material_config[mid]["reward"]
    result = {}
    for _ in range(num):        
        reward_num = random.randint(reward['num'][0], reward['num'][1])
        reward_copy = copy.deepcopy(reward)
        reward_copy.pop('num')
        reward_list = utils.random_choice(reward_copy.keys(),reward_num)
        for reward_id in reward_list:            
            reward_type, reward_result = __get_award(oc_user,reward[reward_id])
            if reward_type == 'equip':
                if not reward_type in result:
                    result[reward_type] = {}
                result[reward_type].update(reward_result)
                 
            elif reward_type == 'item':
                if not reward_type in result:
                    result[reward_type] = []   
                result[reward_type].append(reward_result)
                 
            elif reward_type == 'coin':
                if not reward_type in result:
                    result[reward_type] = []
                result[reward_type].append(reward_result)
             
            elif reward_type == 'diamond':
                if not reward_type in result:
                    result[reward_type] = []
                result[reward_type].append(reward_result)
                 
            elif reward_type == 'cp':
                if not reward_type in result:
                    result[reward_type] = []
                result[reward_type].append(reward_result)
    user_material_obj.minus_material(mid,num)
    return 0, {"msg":result}

def __boss(oc_user,params):
    """消耗boss挑战卷
    """
    mid = params['mid']
    num = int(params['num'])
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    material = user_material_obj.materials.get(mid)
    if not material:
        return 2,{"msg":"您还没有获得该道具"}
    
    if int(material["num"]) < num:
        return 3,{"msg":"您的道具不足"}
    
    #消耗道具
    user_material_obj.minus_material(mid,num)
    
    #添加boss挑战次数
    user_dungeon_obj = UserDungeon.get(oc_user.uid)
    user_dungeon_obj.dungeon_info['dun_boss_num'] = user_dungeon_obj.dungeon_info['dun_boss_num'] + num
    user_dungeon_obj.put()
    return 0,{"msg":{"dun_boss_num":user_dungeon_obj.dungeon_info['dun_boss_num']}}

def __open_dungeon_box(oc_user,params):
    """战场掉落的宝箱
    """
    mid = params['mid']
    num = int(params['num'])
    material_config = game_config.material_config
    need_item = material_config[mid]["need_item"]
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    if int(num) > user_material_obj.materials.get(need_item,0):
        return False    

    #添加奖励
    reward = material_config[mid]["reward"]
    result = {}
    for _ in range(int(num)):        
        reward_num = random.randint(reward['num'][0], reward['num'][1])
        reward_copy = copy.deepcopy(reward)
        reward_copy.pop('num')
        reward_list = utils.random_choice(reward_copy.keys(),reward_num)
        for reward_id in reward_list:            
            reward_type, reward_result = __get_award(oc_user,reward[reward_id])
            if reward_type == 'equip':
                if not reward_type in result:
                    result[reward_type] = {}
                result[reward_type].update(reward_result)
                 
            elif reward_type == 'item':
                if not reward_type in result:
                    result[reward_type] = []   
                result[reward_type].append(reward_result)
                 
            elif reward_type == 'coin':
                if not reward_type in result:
                    result[reward_type] = []
                result[reward_type].append(reward_result)
             
            elif reward_type == 'diamond':
                if not reward_type in result:
                    result[reward_type] = []
                result[reward_type].append(reward_result)
                 
            elif reward_type == 'cp':
                if not reward_type in result:
                    result[reward_type] = []
                result[reward_type].append(reward_result)                
    user_material_obj.minus_material(need_item,num)
    return 0, {"msg":result}

def __get_award(oc_user,item):
    """给奖励
    """
    reward_type = item["type"]
    it = None
    if reward_type == 'equip':
        from apps.models.user_equipments import UserEquipments
        user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
        eid = item["id"]
        property_obj = UserProperty.get(oc_user.uid)
        lv = property_obj.property_info['lv']
        lv = ((lv - 1) / 5 + 1) * 5
        quality = item["grade"]
        eqdbid, equipment = user_equipments_obj.add_equipment(eid,int(quality))
        it = {eqdbid: equipment}
        
    elif reward_type == 'item':
        mid = item["id"]
        num = item["num"]
        lv = oc_user.property_info.property_info["lv"]
        user_material_obj = UserMaterial.get_instance(oc_user.uid)
        #如果是强化精华，就*lv
        material_config = game_config.material_config
        mtype = material_config[mid]["type"]        
        if mtype == '4':
            num = int(num * lv) + 1            
        material = user_material_obj.add_material(mid, num)        
        material = copy.deepcopy(material)
        material[mid]["num"] = num
        it = material
        
    elif reward_type == 'coin':
        money = item["num"]
        property_obj = UserProperty.get(oc_user.uid)
        lv = property_obj.property_info['lv']
        money = int(money * lv)
        property_obj.add_coin(money)
        it = money
        
    elif reward_type == 'cp':
        #荣誉值
        cp = item["num"]
        property_obj = UserProperty.get(oc_user.uid)
        property_obj.add_cp(cp)
        property_obj.put()
        it = cp
        
    elif reward_type == 'diamond':
        diamond = item["num"]
        property_obj = UserProperty.get(oc_user.uid)
        property_obj.add_diamond(diamond)
        property_obj.put()
        it = diamond
    return reward_type, it

def __special_equip_compose(oc_user,params):
    """神器碎片合成
    """
    mid = params['mid']
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    material_config = game_config.material_config
    need_num = material_config[mid]["need_num"]
    #消耗道具
    if user_material_obj.minus_material(mid,need_num):
        return 2,{"msg":u"您的神器碎片不足"}
    #加神器   
    user_lv = self.user_base.property_info.lv
    equip_lv = (user_lv / 5) * 5  if (user_lv / 5) * 5 else 1 
    equip_list = game_config.equipment_lv_config[str(equip_lv)]
    eid = utils.random_choice(equip_list,1)[0]
    user_equipments_obj = UserEquipments.get(oc_user.uid)
    eqdbid,equipment = user_equipments_obj.add_equipment(eid,5,special_num=1)
    return 0,{"result":{eqdbid:equipment}}