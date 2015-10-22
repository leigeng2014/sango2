#-*- coding: utf-8 -*-
from apps.config import game_config
from apps.models.user_shop import UserShop
from apps.models.user_property import UserProperty
from apps.models.user_material import UserMaterial
from apps.models.user_equipments import UserEquipments

def cp_shop_info(oc_user,params):
    """荣誉商店首页
    """
    data = {}
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    data["result"] = user_shop_obj.cp_shop
    data["refresh_num"] = user_shop_obj.cp_refresh_num
    data["refresh_cost"] = game_config.cp_shop_config.get("renew_cost",{"1":50})
    return 0,data

def cp_shop_refresh(oc_user,params):
    """刷新荣誉商店
    """
    data = {}
    cp_shop_config = game_config.cp_shop_config
    renew_cost = cp_shop_config["renew_cost"]
    #增加刷新次数
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    user_shop_obj.cp_refresh_num += 1    
 
    cost = 0
    if str(user_shop_obj.cp_refresh_num) in renew_cost:
        cost = renew_cost[str(user_shop_obj.cp_refresh_num)] 
    else:
        cost = max(renew_cost.values()) 
    
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.property_info["cp"] < cost:
        return 1,{"msg":"not enough cp"}
       
    user_property_obj.property_info["cp"] -= cost
    user_property_obj.put() 
    user_shop_obj.put()
    #刷新结果  
    data["result"] = user_shop_obj.cp_refresh("special")
    data["refresh_num"] = user_shop_obj.cp_refresh_num
    return 0,data

def cp_shop_buy(oc_user,params):
    """荣誉商店购买
    """    
    data = {}
    sid = str(params["sid"])
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    cp_shop = user_shop_obj.cp_shop    
    if sid not in cp_shop:
        return 1,{"msg":"this item is not exist"}
    
    cost = cp_shop[sid]["cost"]
    item_id = cp_shop[sid]["id"]
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.property_info.setdefault("cp",1000) < cost:
        return 2,{"msg":"not enough cp"}

    #消耗荣誉
    user_property_obj.property_info["cp"] -= cost
    user_property_obj.put() 
    #添加道具
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    data["items"] = user_material_obj.add_material(item_id)
    #删掉此道具，如果cp_shop买空，则重新刷新
    cp_shop.pop(sid)    
    data["result"] = {}
    if not cp_shop:
        data["result"] = user_shop_obj.cp_refresh() 
    user_shop_obj.put()
    return 0,data

def common_shop_info(oc_user,params):
    """商店首页
    """
    data ={}
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    data["result"] = user_shop_obj.common_shop
    data["refresh_num"] = user_shop_obj.common_refresh_num
    data["refresh_cost"] = game_config.shop_extra_config.get("refresh_cost",{"1":50})
    data["coin_buy_num"] = 1   #弃用
    data["buy_coin_num"] = user_shop_obj.buy_coin_num #今天买金币的次数
    coin_shop = game_config.shop_extra_config["coin_shop"]
    data["coin"] = oc_user.property_info.property_info["lv"] * coin_shop["coin_base"]
    data["cost"] = coin_shop["cost"]
    return 0,data

def common_shop_refresh(oc_user,params):
    """刷新商店
    """
    data = {}
    shop_config = game_config.shop_extra_config
    refresh_cost_config = shop_config["refresh_cost"]
    
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    user_shop_obj.common_refresh_num += 1
    cost = 0
    if str(user_shop_obj.common_refresh_num) in refresh_cost_config:
        cost = refresh_cost_config[str(user_shop_obj.common_refresh_num)] 
    else:
        cost = max(refresh_cost_config.values()) 
    
    user_property_obj = UserProperty.get(oc_user.uid)
    if user_property_obj.property_info["diamond"] < cost:
        return 1,{"msg":"not enough diamond"}
       
    user_property_obj.property_info["diamond"] -= cost
    user_property_obj.put() 
    user_shop_obj.put()
    #刷新结果  
    data["result"] = user_shop_obj.common_refresh()
    data["refresh_num"] = user_shop_obj.common_refresh_num
    return 0,data

def common_shop_buy(oc_user,params):
    """商店购买
    """    
    data = {}
    sid = str(params["sid"])
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    common_shop = user_shop_obj.common_shop    
    if sid not in common_shop:
        return 1,{"msg":"this item is not exist"}
    
    cost = common_shop[sid]["cost"]
    _id = common_shop[sid]["id"]
    _type = common_shop[sid]["type"]
    cost_type = common_shop[sid]["cost_type"]
    if cost_type == "coin":
        if not oc_user.property_info.minus_coin(cost):
            return 2,{"msg":"not enough coin"}
        
    if cost_type == "diamond":
        if not oc_user.property_info.minus_diamond(cost):
            return 3,{"msg":"not enough diamond"}
        
    #添加道具
    data["get_items"] = {}
    if _type == "item":       
        num = common_shop[sid]["num"] 
        user_material_obj = UserMaterial.get_instance(oc_user.uid)
        data["get_items"]["items"] = user_material_obj.add_material(_id,num)
    else:
        #lv = common_shop[sid]["lv"]
        quality = common_shop[sid]["quality"]
        _type = common_shop[sid]["type"]
        num = common_shop[sid]["num"]
        for _ in range(num):
            user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
            eqdbid,equipment = user_equipments_obj.add_equipment(_id,quality,add_type="shop")
            if data["get_items"].get("equipments"):
                data["get_items"]["equipments"].update({eqdbid:equipment})
            else:
                data["get_items"]["equipments"] = {eqdbid:equipment}
        
    #删掉此道具，如果cp_shop买空，则重新刷新
    common_shop.pop(sid) 
    user_shop_obj.put()
    data["result"] = {}
    if not common_shop:
        data["result"] = user_shop_obj.common_refresh()
    return 0,data

def common_shop_buy_all(oc_user,params):
    """商店购买全部
    """    
    data = {}
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    common_shop = user_shop_obj.common_shop    
    cost_diamond = sum([common_shop[sid]["cost"] for sid in common_shop  if common_shop[sid]["cost_type"] == "diamond"])
    cost_coin = sum([common_shop[sid]["cost"] for sid in common_shop if common_shop[sid]["cost_type"] == "coin"])
    #消耗钻石和coin
    if cost_diamond > 0:
        if not oc_user.property_info.minus_diamond(cost_diamond):
            return 1,{"msg":"not enough coin"}
        
    if cost_coin > 0:
        if not oc_user.property_info.minus_coin(cost_coin):
            return 2,{"msg":"not enough diamond"}

    #添加道具    
    data["get_items"] = {}
    for sid in common_shop:
        _id = common_shop[sid]["id"]
        _type = common_shop[sid]["type"]
        if _type == "item":       
            num = common_shop[sid]["num"] 
            user_material_obj = UserMaterial.get_instance(oc_user.uid)
            material = user_material_obj.add_material(_id,num)
            
            mid = material.keys()[0]
            if mid not in data["get_items"].setdefault("items",{}):
                data["get_items"]["items"].update(material)
            else:
                data["get_items"]["items"][mid]["num"] += num 
        else:
            #lv = common_shop[sid]["lv"]
            quality = common_shop[sid]["quality"]
            _type = common_shop[sid]["type"]
            num = common_shop[sid]["num"] 
            for _ in range(num):
                user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
                eqdbid,equipment = user_equipments_obj.add_equipment(_id,quality)
                if data["get_items"].get("equipments"):
                    data["get_items"]["equipments"].update({eqdbid:equipment})
                else:
                    data["get_items"]["equipments"] = {eqdbid:equipment}
        
    #删掉此道具，如果cp_shop买空，则重新刷新
    data["result"] = user_shop_obj.common_refresh()
    return 0,data

def buy_coin(oc_user,params):
    """购买金币
    """
    btype = params.get('type','1') #1 为单个购买，2为全部购买    
    user_property_obj = UserProperty.get(oc_user.uid)
    user_shop_obj = UserShop.get_instance(oc_user.uid)
    vip_config = game_config.vip_config[user_property_obj.vip_lv]
    buyCoin_num = vip_config["buyCoin_num"]
    if buyCoin_num <= user_shop_obj.buy_coin_num:
        return 1,{"msg":"您购买次数已经用完了"}
    
    num = 1
    if btype == '2':
        num = buyCoin_num - user_shop_obj.buy_coin_num        
    coin_shop = game_config.shop_extra_config["coin_shop"]
    cost = int(coin_shop["cost"] * num)
    
    if user_property_obj.property_info["diamond"] < cost:
        return 1,{"msg":"your diamond is not enough"} 
    
    #消耗钻石，加金币
    user_property_obj.minus_diamond(cost)
    coin = user_property_obj.property_info["lv"] * coin_shop["coin_base"]
    user_property_obj.add_coin(coin * num)
    user_shop_obj.buy_coin_num += num
    user_shop_obj.put()
    return 0,{}