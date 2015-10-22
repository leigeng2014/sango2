#-*- coding: utf-8 -*-
import math
import copy
import random

from apps.common import utils
from apps.config import game_config
from apps.models.user_equipments import UserEquipments
from apps.models.user_forge import UserForge
from apps.models.user_property import UserProperty
from apps.models.user_material import UserMaterial
from apps.models.user_cards import UserCards
from apps.models.user_teams import UserTeams

def puton(oc_user, params):
    """穿装备
    """    
    eqdbid = params['eqdbid'] #装备id
    cid = params['cid']       #装备的角色
    part = params['part']     #装备的部位
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipment = user_equipments_obj.equipments.get(eqdbid)
    #判断装备存在不存在
    if not equipment:
        return 1,{"msg":"this equipment is not exist"}
    #判断该装备是否已经被装备
    if eqdbid in user_equipments_obj.get_puton_equip():
        return 2,{"msg":"this equipment has puton yet"}
    #判断该装备类型是否能穿
    equip_config = game_config.equipment_config[equipment["eid"]]
    equip_category = equip_config["category"]
    if equip_category != '0': 
        if cid == '0':              
            user_cards_obj = UserCards.get(oc_user.uid)
            category = user_cards_obj.category
        else:
            user_teams_obj = UserTeams.get(oc_user.uid)
            category = user_teams_obj.category(cid)
        if equip_category != category:
            return 3,{"msg":"you can't put on this category equipment"}
        
    #判断该装备的等级是否满足
    elv = equipment["lv"]
    lv = oc_user.property_info.property_info["lv"]
    if elv > (lv + 10):
        return 4,{"msg":"lv > 10"}  
    user_equipments_obj.put_on(eqdbid,part,cid)
    #称号     
    from apps.models.user_title import UserTitle
    user_title_obj = UserTitle.get_instance(oc_user.uid)
    user_title_obj.set_title('4')
    return 0, {"msg": True}   

def puton_all(oc_user, params):
    """一键穿装备
    """    
    eqdbid = params['eqdbid'] #装备id
    cid = params['cid']       #装备的角色
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipments = user_equipments_obj.equipments
    #判断该装备类型是否能穿
    eqdbid_list = eqdbid.split(',')
    for eq in eqdbid_list:
        if eq not in equipments:
            continue
        equipment = equipments[eq]
        eid = equipment["eid"]
        equip_config = game_config.equipment_config[eid]
        equip_type = equip_config["type"]
        user_equipments_obj.put_on(eq,equip_type,cid) 
    #称号     
    from apps.models.user_title import UserTitle
    user_title_obj = UserTitle.get_instance(oc_user.uid)
    user_title_obj.set_title('4')               
    return 0,{}  

def takeoff(oc_user, params):
    """脱装备
    """
    eqdbid = params['eqdbid']
    cid = params['cid']
    part = params['part']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    user_equipments_obj.take_off(eqdbid, part, cid)
    return 0,{"msg": True}

def getall(oc_user, params):
    """获取所有装备
    """
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    data = user_equipments_obj.equipments
    return 0,{"equipments": data}

def singleSell(oc_user, params):  
    """卖单个装备
    """  
    eqdbid = params['eqdbid']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    money = user_equipments_obj.single_sell(eqdbid)
    return 0, {"msg": money}

def batchSell(oc_user, params):
    """卖装备，按品质
    """    
    quality = int(params['quality'])
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    money = user_equipments_obj.batch_sell(quality)
    return 0, {"msg": money}

def strengthen(oc_user, params):
    """装备强化
    """    
    eqdbid = params['eqdbid']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipment = user_equipments_obj.equipments.get(eqdbid, {})
    if not equipment:
        return 1,{"msg":"this equipment is not exist"}

    eid = equipment["eid"]
    lv = equipment["lv"]
    quality = equipment["quality"]
    minilv = equipment["minilv"]
    equipment_config = game_config.equipment_config[eid]
    _type = equipment_config['type']    
    strengthen_config = game_config.equipment_strengthen_config
    #强化所需要的基础配置消耗
    equip_influence = strengthen_config['equip_influence'][_type]
    minilv += 1
    if minilv > len(equip_influence):
        return 2,{"msg":"this equipment can't strengthen"}
    
    equipment["minilv"] = minilv
    eq_minilv_growth = equip_influence[str(minilv)]
    class_influence = strengthen_config['class_influence'][str(quality)]
    growth_multiplier = class_influence['growth_multiplier']
    #随着等级改变 金币的变化
    coin = int(
        math.ceil(
            ( (lv - 1)
              * eq_minilv_growth['coin_growth']
              + eq_minilv_growth['coin']
            ) * growth_multiplier
        )
    )    
    #现在知道了消耗的金钱和材料的数量
    property_obj = UserProperty.get(oc_user.uid)
    if not property_obj.minus_coin(coin):
        return 3,{"msg":"you have not enough coin"}
    
    mid, base_num = eq_minilv_growth["item"]
    growth_num = eq_minilv_growth["item_growth"]
    #随着等级改变 材料数量的变化
    final_num = ((lv - 1) * growth_num + base_num) * growth_multiplier
    final_num = int(math.ceil(final_num))
    material_obj = UserMaterial.get(oc_user.uid)
    if material_obj.materials.get(mid,{}).get("num",0) < final_num:
        return 4,{"msg":"you have not enough material"}
    
    material_obj.minus_material(mid, final_num)
    if not "strenth_cast" in equipment:
        equipment["strenth_cast"] = ("0", 0)
    equipment["strenth_cast"] = (mid, equipment["strenth_cast"][1] + final_num)
    user_equipments_obj.put() 
    return 0, {"msg": equipment}

def roll(oc_user, params):
    """普通洗练
    """    
    eqdbid = params['eqdbid']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipment = user_equipments_obj.equipments.get(eqdbid)
    if not equipment:
        return 1,{"msg":"this equipment is not exist"}    
         
    lv = equipment["lv"]
    quality = equipment["quality"]
    if quality < 3 or lv < 10:
        return 2,{"msg":"this equipment can't roll"}
    
    #消耗金钱
    equipment_forge_config = game_config.equipment_forge_config
    cost_base = equipment_forge_config["shuffle_costBase"] #洗练消耗金币初始
    cost_growth = equipment_forge_config["shuffle_costGrowth"] #洗练消耗金币初始
    cost_coin = int(cost_base + (lv-1)* cost_growth)    
    user_property_obj = UserProperty.get(oc_user.uid)    
    if user_property_obj.property_info["coin"] < cost_coin:
        return 3,{"msg":"you have not enough coin"}    
    user_property_obj.minus_coin(cost_coin)
    
    #开始计算属性
    vice_attr = equipment["vice_attr"]
    total = 0
    keyary = []
    for k, v in vice_attr.items():
        total += v
        keyary.append(k)
        
    if len(vice_attr) == 2:
        value_ary = []
        #向上取整
        purple_min = int(total * 0.0833 + 1)
        purple_max = int(total * 0.833)
        limit_up = total - purple_min # 2 - 1 1x
        if limit_up > purple_max:
            limit_up = purple_max

        limit_down = total - purple_max
        if limit_down > purple_min:
            purple_min = limit_down
        result = random.randint(purple_min, limit_up)
        value_ary.append(result)
        _total = total - result
        value_ary.append(_total)
        
    elif len(vice_attr) == 3:
        value_ary = []
        #向上取整
        purple_min = int(total * 0.0625 + 1)
        purple_max = int(total * 0.625)
        limit_up = total - 2 * purple_min # 3 - 1
        if limit_up > purple_max:
            limit_up  = purple_max
            
        result = random.randint(purple_min, limit_up)
        value_ary.append(result)
        _total = total - result
        limit_up = _total - purple_min
        if limit_up > purple_max:
            limit_up = purple_max

        limit_down = _total - purple_max
        if limit_down > purple_min:
            purple_min = limit_down

        result = random.randint(purple_min, limit_up)
        value_ary.append(result)
        _total = _total - result
        value_ary.append(_total)
    else:
        value_ary = []
        #向上取整
        purple_min = int(total * 0.05 + 1)
        purple_max = int(total * 0.5)
        limit_up = total - 3 * purple_min # 4 - 1
        if limit_up > purple_max:
            limit_up  = purple_max
        result = random.randint(purple_min, limit_up)  #第一次
        value_ary.append(result)
        _total = total - result
        limit_up = _total - 2 * purple_min  # 4 - 2

        if limit_up > purple_max:
            limit_up = purple_max

        result = random.randint(purple_min, limit_up)  #第二次
        value_ary.append(result)
        _total = _total - result
        limit_up = _total - 1 * purple_min  # 4 - 3
        if limit_up > purple_max:
            limit_up = purple_max

        limit_down = _total - purple_max
        if limit_down > purple_min:
            purple_min = limit_down

        result = random.randint(purple_min, limit_up)  #第三次
        value_ary.append(result)
        _total = _total - result                      #第四次
        value_ary.append(_total)

    for x in range(len(vice_attr)):
        key = keyary[x]
        vice_attr[key] = value_ary[x]

    user_equipments_obj.put()
    return 0, {"msg": equipment}

def advanced_roll(oc_user, params):
    """高级洗练
    """    
    ueid = params['ueid']
    eqdbid = ueid
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipment = user_equipments_obj.equipments.get(eqdbid)
    if not equipment:
        return 1,{"msg":"this equipment is not exist"}    
         
    lv = equipment["lv"]
    quality = equipment["quality"]
    if quality < 3 or lv < 10:
        return 2,{"msg":"this equipment can't roll"}
    
    #消耗金钱
    equipment_forge_config = game_config.equipment_forge_config
    cost_base = equipment_forge_config["shuffle_costBase"] #洗练消耗金币初始
    cost_growth = equipment_forge_config["shuffle_costGrowth"] #洗练消耗金币初始
    cost_coin = int(cost_base + (lv-1)* cost_growth)    
    user_property_obj = UserProperty.get(oc_user.uid)    
    if user_property_obj.property_info["coin"] < cost_coin:
        return 3,{"msg":"you have not enough coin"}    
    user_property_obj.minus_coin(cost_coin)
    
    #开始计算属性
    vice_attr = equipment["vice_attr"]
    total = 0
    keyary = []
    for k, v in vice_attr.items():
        total += v
        keyary.append(k)
        
    if len(vice_attr) == 2:
        value_ary = []
        #向上取整
        purple_min = int(total * 0.0833 + 1)
        purple_max = int(total * 0.833)
        limit_up = total - purple_min # 2 - 1 1x
        if limit_up > purple_max:
            limit_up = purple_max

        limit_down = total - purple_max
        if limit_down > purple_min:
            purple_min = limit_down
        result = random.randint(purple_min, limit_up)
        value_ary.append(result)
        _total = total - result
        value_ary.append(_total)
        
    elif len(vice_attr) == 3:
        value_ary = []
        #向上取整
        purple_min = int(total * 0.0625 + 1)
        purple_max = int(total * 0.625)
        limit_up = total - 2 * purple_min # 3 - 1
        if limit_up > purple_max:
            limit_up  = purple_max
            
        result = random.randint(purple_min, limit_up)
        value_ary.append(result)
        _total = total - result
        limit_up = _total - purple_min
        if limit_up > purple_max:
            limit_up = purple_max

        limit_down = _total - purple_max
        if limit_down > purple_min:
            purple_min = limit_down

        result = random.randint(purple_min, limit_up)
        value_ary.append(result)
        _total = _total - result
        value_ary.append(_total)
    else:
        value_ary = []
        #向上取整
        purple_min = int(total * 0.05 + 1)
        purple_max = int(total * 0.5)
        limit_up = total - 3 * purple_min # 4 - 1
        if limit_up > purple_max:
            limit_up  = purple_max
        result = random.randint(purple_min, limit_up)  #第一次
        value_ary.append(result)
        _total = total - result
        limit_up = _total - 2 * purple_min  # 4 - 2

        if limit_up > purple_max:
            limit_up = purple_max

        result = random.randint(purple_min, limit_up)  #第二次
        value_ary.append(result)
        _total = _total - result
        limit_up = _total - 1 * purple_min  # 4 - 3
        if limit_up > purple_max:
            limit_up = purple_max

        limit_down = _total - purple_max
        if limit_down > purple_min:
            purple_min = limit_down

        result = random.randint(purple_min, limit_up)  #第三次
        value_ary.append(result)
        _total = _total - result                      #第四次
        value_ary.append(_total)

    for x in range(len(vice_attr)):
        key = keyary[x]
        vice_attr[key] = value_ary[x]

    user_equipments_obj.put()
    return 0, {"equipment": equipment}

def punch(oc_user, params):
    """打孔
    """    
    eqdbid = params['eqdbid']
    index = int(params["index"])
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipment = user_equipments_obj.equipments[eqdbid]
    #判断装备是否存在
    if not equipment:
        return 1,{"msg":"this equipment is not exist"}    
    #判断是否已经开过
    gem_hole = equipment["gem_hole"]
    if gem_hole[index-1] != 0:
        return 2,{"msg":u"该宝石孔已经开过了"}
    #判断上一个是否开启
    if (index > 1) and (gem_hole[index-2] == 0):
        return 3,{"msg":u"请开上一个孔"}
    
    gemSlot_unlock = game_config.gem_config["gemSlot_unlock"]
    cfg = gemSlot_unlock[str(index)]
    coin_base = cfg['coin_base']
    item = cfg['item']    
    #判断金钱是否充足
    lv = equipment["lv"]
    coin = coin_base * lv
    user_property_obj = UserProperty.get(oc_user.uid)
    if not user_property_obj.minus_coin(coin):
        return 4,{"msg":u"金币不够"}    
    #判断道具是否充足
    if len(item) != 0:
        mid, num = item        
        user_material_obj = UserMaterial.get(oc_user.uid)
        if (mid not in user_material_obj.materials) or \
            ((mid in user_material_obj.materials) and  \
            (user_material_obj.materials[mid]["num"] < int(num))):
            return 5,{"msg":u"材料不足"}
        user_material_obj.minus_material(mid, int(num))
        
    gem_hole[index-1] = 1
    user_equipments_obj.put()        
    return 0, {"msg": equipment}

def embed(oc_user, params):
    """嵌入和脱下宝石
    """   
    eqdbid = params['eqdbid']    
    mid = params['mid']
    location = int(params['location'])
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    if eqdbid not in user_equipments_obj.equipments:
        return 1, {"msg":u"装备不存在"}
    equipment = user_equipments_obj.equipments[eqdbid]
    gem_hole = equipment["gem_hole"]
    if gem_hole[location] == 0:
        return 2,{"msg":u"孔没开"}
    
    #mid为''代表脱掉宝石，不为空代表嵌入宝石
    material_obj = UserMaterial.get(oc_user.uid)
    if mid == "":
        if gem_hole[location] == 1:
            return 3,{"msg":u"该孔没有嵌入宝石"}               
        material_obj.add_material(gem_hole[location], 1)
        gem_hole[location] = 1 
    else:
        if gem_hole[location] != 1:
            return 4,{"msg":u"该孔已经嵌入宝石!"}
        
        if mid not in material_obj.materials:
            return 5,{"msg":u"该宝石不存在"}
        
        if material_obj.materials[mid]["type"] != '1':
            return 6,{"msg":u"请镶嵌宝石"}
        
        material_obj.minus_material(mid, 1)
        #返回True代表没有相同的宝石
        def has_same_gem(mid):
            gem_effect = set({})
            cfg = game_config.material_config
            for position in range(len(gem_hole)):
                value = gem_hole[position]
                if isinstance(value, int):
                    continue
                gem_effect.add(cfg[value]['gem_effect'])
            if cfg[mid]['gem_effect'] in gem_effect:
                return False
            return True
           
        tof = has_same_gem(mid)
        if not tof:
            return 7, {"msg":u"不能有相同颜色的宝石"}
        gem_hole[location] = mid
    user_equipments_obj.put()
    return 0, {"msg": equipment}

def allunembed(oc_user, params):
    """一键脱下所有宝石
    """    
    eqdbid = params['eqdbid']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    equipment = user_equipments_obj.equipments.get(eqdbid)
    if not equipment:
        return 1,{"msg":u"没有这个装备"}
    
    gem_hole = equipment["gem_hole"]
    material_obj = UserMaterial.get(oc_user.uid)
    for position in range(len(gem_hole)):
        if gem_hole[position] not in [0,1]:            
            material_obj.add_material(gem_hole[position], 1) 
            gem_hole[position] = 1           
    user_equipments_obj.put()
    return 0, {"msg": equipment}

def smelting(oc_user, params):
    """熔炼
    """
    multi = params['multi']
    eqdbids = multi.split(',')
    eqdbids = filter(lambda x: x, eqdbids)
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    smelting_config = game_config.equipment_smelting_config
    result = {}
    result["eqPoint"] = 0 
    result["equipments"] = {}
    result["items"] = []    #主要用来存储强化晶石
    equipment_lv_config = game_config.equipment_lv_config
    material_obj = UserMaterial.get(oc_user.uid)
    for eqdbid in eqdbids:
        equipment = user_equipments_obj.equipments.get(eqdbid, False)
        if equipment:
            eid = equipment["eid"]
            lv = equipment["lv"]
            minilv = equipment["minilv"]
            quality = equipment["quality"]
            user_equipments_obj.equipments.pop(eqdbid)
            #如果有强化晶石，则返回给玩家
            if minilv != 0:
                mid, num = equipment["strenth_cast"]
                material = material_obj.add_material(mid, num)
                result["items"].append(material) 
                
            #如果有宝石，则返回宝石给玩家
            for v in equipment["gem_hole"].values():
                if v not in [0,1]:
                    material = material_obj.add_material(v, 1)
                    result["items"].append(material)
                
            equip_cfg = smelting_config[str(quality)]['equip']
            eqPoint_cfg = smelting_config[str(quality)]['eqPoint']
            back = utils.get_item_by_random_simple([("equip",equip_cfg['weight']),\
                                                    ("eqPoint",eqPoint_cfg['weight'])])   
            #熔炼值 
            if back == 'eqPoint':
                result['eqPoint'] += eqPoint_cfg['num']
            #装备
            else:
                back_lv = utils.get_item_by_random_simple(equip_cfg['lv'].items())
                back_quality = utils.get_item_by_random_simple(equip_cfg['quality'].items())    
                if back_lv == "minus_weight":
                    new_lv = lv - 5  if lv - 5 > 0 else 1
                else:
                    new_lv = lv    
                if back_quality == "add_weight":
                    new_quality = quality + 1
                    if new_quality > 5:
                        new_quality = 5
                else:
                    new_quality = quality
                eid = utils.random_choice(equipment_lv_config[str(new_lv)], 1)[0]
                eqdbid,equipment = user_equipments_obj.add_equipment(eid,new_quality,add_type="smelting")
                result["equipments"][eqdbid] = equipment
    #加熔炼值            
    if result["eqPoint"] > 0:            
        property_obj = UserProperty.get(oc_user.uid)
        property_obj.add_smelting(result["eqPoint"])
        
    #保存装备
    user_equipments_obj.put()
    return 0, {"msg": result}

def devour(oc_user,params):
    """神器吞噬
    """
    base_ueid = params['base_ueid']
    cost_ueids = params['cost_ueids']
    cost_ueids = cost_ueids.split(',')
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    exp = 0
    for ueid in cost_ueids:
        exp += user_equipments_obj.get_special_devour_exp(ueid)
        user_equipments_obj.equipments.pop(ueid)
    user_equipments_obj.put() 
    equipment = user_equipments_obj.add_special_exp(base_ueid,exp) 
    return 0, {"equipment":equipment}

def smriti(oc_user,params):
    """神器传承
    """
    base_ueid = params['base_ueid']
    cost_ueid = params['cost_ueid']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    cost_special_attr = user_equipments_obj.equipments[base_ueid]["special_attr"]
    user_equipments_obj.equipments[cost_ueid]["special_attr"] = copy.deepcopy(cost_special_attr)
    user_equipments_obj.equipments[base_ueid]["special_attr"] = {}
    user_equipments_obj.put()
    
    return 0, {"equipment":user_equipments_obj.equipments[base_ueid]}
    
def fuse(oc_user,params):
    """神器融合(变成双属性)
    """
    base_ueid = params['base_ueid']
    cost_ueid = params['cost_ueid']
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    cost_special_attr = user_equipments_obj.equipments[base_ueid]["special_attr"]
    user_equipments_obj.equipments[base_ueid]["special_attr"]['2'] = copy.deepcopy(cost_special_attr['1'])
    user_equipments_obj.equipments[cost_ueid]["special_attr"] = {}
    user_equipments_obj.put()
    return 0, {"equipment":user_equipments_obj.equipments[base_ueid]}

def forge_info(oc_user,params):
    """打造的装备信息
    """
    data = {}
    user_forge_obj = UserForge.get_instance(oc_user.uid)
    data["forge_equipment"] = user_forge_obj.equipments
    data["forge_free_times"] = user_forge_obj.free_times
    data["forge_cost_smelting"] = user_forge_obj.cost_smelting
    return 0,data
    
def forge_refresh(oc_user, params):
    """刷新打造装备
    """
    data = {}
    user_forge_obj = UserForge.get_instance(oc_user.uid)
    forge_config = game_config.equipment_forge_config
    refresh_cost = forge_config["refresh_cost"]
    if user_forge_obj.free_times == 0:
        user_property_obj = UserProperty.get(oc_user.uid)
        if refresh_cost > user_property_obj.property_info["diamond"]:
            return 1,{"msg":"diamond is not enough"}
        user_property_obj.minus_diamond(int(refresh_cost))
    else:
        user_forge_obj.free_times -= 1  
        user_forge_obj.put()
    #计算打造的装备和需要的熔炼值
    cost_smelting,eqdbid,equipment = user_forge_obj.forge()
    data["forge_cost_smelting"] = cost_smelting
    data["forge_free_times"] = user_forge_obj.free_times
    data["equipments"] = {eqdbid:equipment}    
    return 0,data

def forge_buy(oc_user,params):
    """购买打造的装备
    """
    data = {}
    user_forge_obj = UserForge.get_instance(oc_user.uid)
    user_property_obj = UserProperty.get(oc_user.uid)
    cost_smelting = user_forge_obj.cost_smelting
    user_smelting = user_property_obj.property_info.get("smelting",0)
    if cost_smelting > user_smelting:
        return 1,{"msg":"smelting is not enough"}
    #消耗熔炼值
    user_property_obj.property_info["smelting"] -= cost_smelting
    user_property_obj.put()
    #加装备
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    user_equipments_obj.equipments.update(user_forge_obj.equipments)
    user_equipments_obj.put()
    
    data["equipments"] = user_forge_obj.equipments
    cost_smelting,eqdbid,equipment = user_forge_obj.forge()
    data["forge_cost_smelting"] = cost_smelting
    data["forge_free_times"] = user_forge_obj.free_times
    data["new_equipments"] = {eqdbid:equipment}
    return 0,data    

def extend_num(oc_user,params):
    """军营扩容
    """
    num = int(params.get("num",1))
    system_config = game_config.system_config
    equipNum_limit = system_config["equipNum_limit"]
    equipExpand_cost = system_config["equipExpand_cost"]
    equipExpand_num = system_config["equipExpand_num"]
    equipExpand_limit = system_config["equipExpand_limit"]
    max_num = equipNum_limit + (equipExpand_num * equipExpand_limit)
    if oc_user.property_info.property_info["max_card_num"] >= max_num:
        return 1,{"msg":u"已到达最大的格子数量"}
    if oc_user.property_info.property_info["diamond"] <= equipExpand_cost:
        return 2,{"msg":u"钻石不足"}

    oc_user.property_info.minus_diamond(equipExpand_cost * num)
    oc_user.property_info.property_info["max_card_num"] += (equipExpand_num * num)
    oc_user.property_info.put()
    return 0,{}

def equip_setting(oc_user,params):
    """挂机设置
    """
    settings = params["settings"]
    settings = settings.split(',')
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    user_equipments_obj.equip_settings = [int(i) for i in settings if i in ['0','1','2','3','4']]
    user_equipments_obj.put()
    return 0,{}

def special_forge_info(oc_user,params):
    """神器打造列表
    """
    data = {}
    special_forge_config = {'1':{"smelting":20000,"popularity":2000},'2':{"smelting":20000,"popularity":20000}}
       
    data["special_forge_config"] = special_forge_config
    data["equip_list"] = {}
    user_forge_obj = UserForge.get_instance(oc_user.uid)
    #更新神器打造列表 
    user_forge_obj.special_forge()
    if not user_forge_obj.special_equipments:
        user_forge_obj.special_forge()
    else:
        user_lv = oc_user.property_info.lv
        equip_lv = (user_lv / 5) * 5  if (user_lv / 5) * 5 else 1
        if equip_lv != user_forge_obj.special_equip_lv:
            user_forge_obj.special_forge()        
 
    data["equip_list"] = user_forge_obj.special_equipments
    return 0,{"result":data}

def special_forge_buy(oc_user,params):
    """神器打造购买
    """
    seid = params.get("seid")
    user_forge_obj = UserForge.get_instance(oc_user.uid)
    special_equip = user_forge_obj.special_equipments[seid]
    special_forge_config = {'1':{"smelting":20000,"popularity":2000},'2':{"smelting":20000,"popularity":20000}}
    cost = special_forge_config[str(len(special_equip["special_attr"]))]
    if not oc_user.property_info.minus_popularity(cost["popularity"]):
        return 1,{"msg":u"你的声望不够"}
    
    if not oc_user.property_info.minus_smelting(cost["smelting"]):
        return 2,{"msg":u"你的熔炼值不够"}
    
    #加装备
    new_equipment = user_forge_obj.special_equipments[seid]
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    eqdbid = utils.create_gen_id()
    user_equipments_obj.equipments.update({eqdbid:new_equipment})
    user_equipments_obj.put()

    return 0,{"result":{eqdbid:new_equipment}}
