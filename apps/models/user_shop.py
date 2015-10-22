#-*- coding: utf-8 -*-
import time
from apps.oclib.model import UserModel
from apps.config import game_config
from apps.common import utils

class UserShop(UserModel):  
    pk = 'uid'
    fields = ['uid','cp_shop','cp_refresh_num','cp_refresh_date','common_shop',\
              'common_refresh_date','common_refresh_num','buy_coin_num',\
              'coin_refresh_date',\
              ]      
    def __init__(self,uid = None):
        """用户商店信息
        """
        self.uid = uid
        self.cp_shop = {}
        self.cp_refresh_num = 0
        self.cp_refresh_date = int(time.time()) 
        self.common_shop = {}
        self.common_refresh_num = 0
        self.common_refresh_date = int(time.time()) 
        self.buy_coin_num = 0 #购买金币的次数
        self.coin_refresh_date = int(time.time())

    @classmethod
    def get_instance(cls,uid):
        obj = super(UserShop,cls).get(uid)        
        if obj is None:
            obj = cls._install(uid)
        return obj
    
    @classmethod
    def get(cls,uid):
        obj = super(UserShop,cls).get(uid)
        return obj
    
    @classmethod
    def _install(cls,uid):
        obj = cls(uid)
        obj.uid = uid
        obj.cp_refresh("common")
        obj.common_refresh()
        obj.put()
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    def cp_refresh(self,ctype="common"):
        """刷新荣誉商店,ctype=common(系统刷新)/special(手动刷新)
        """
        cp_exchange = game_config.cp_shop_config["cp_exchange"]
        if ctype == "common":
            cp_shop_weight = dict([(k,v["common_weight"]) for k,v in cp_exchange.items()])
        else:
            cp_shop_weight = dict([(k,v["special_weight"]) for k,v in cp_exchange.items()]) 
            
        result = {}
        for i in range(6):
            i += 1
            dict_ = {}
            weight_id = self.__weight_back(cp_shop_weight)
            dict_["type"] = cp_exchange[weight_id]["type"]
            dict_["cost"] = cp_exchange[weight_id]["cost_cp"]
            dict_["id"] = cp_exchange[weight_id]["id"]
            result[str(i)] = dict_
        self.cp_shop = result
        self.put()
        return result
    
    def common_refresh(self):
        """普通商店刷新
        """
        result = {}
        sell_item_config = game_config.shop_config["sell_item_config"]
        shop_extra_config = game_config.shop_extra_config
        equipment_lv_config = game_config.equipment_lv_config
        sell_item_weight = dict([(k,v["weight"]) for k,v in sell_item_config.items()])
        user_lv = self.user_base.property_info.property_info["lv"] 
        equip_config = game_config.equipment_config
        for i in range(6):
            i += 1
            temp = {}
            random_type = utils.get_item_by_random_simple(shop_extra_config["shop_weight"].items())
            if random_type == 'equip':
                temp["quality"] = 4 #商店只买紫色装备
                equip_lv = (user_lv / 5) * 5  if (user_lv / 5) * 5 else 1     
                lv_flag = utils.get_item_by_random_simple(shop_extra_config["equip_lv"].items())                    
                if lv_flag == "add_weight":
                    equip_lv = ((user_lv / 5) + 1) * 5                
                temp["lv"] = equip_lv                 
                temp["id"] = utils.random_choice(equipment_lv_config[str(equip_lv)], 1)[0]
                temp["main_attr"] = self.__main_install(temp["id"],equip_lv)
                temp["num"] = 1
                temp["type"] = "equip"
                equip_info = equip_config[temp["id"]]
                cost = 0
                cost_type = ''
                shop_coin = equip_info["shop_coin"]
                shop_diamond = equip_info["shop_diamond"]
                if shop_coin and shop_diamond:
                    if utils.random_choice(['coin','diamond'], 1)[0] == "coin":
                        cost_type = "coin"
                        cost = shop_coin 
                    else:
                        cost_type = "diamond"
                        cost = shop_diamond
                elif shop_coin:
                    cost_type = "coin"
                    cost = shop_coin
                elif shop_diamond:
                    cost_type = "diamond"
                    cost = shop_diamond   
            else:
                weight_id = self.__weight_back(sell_item_weight)
                temp["id"] = sell_item_config[weight_id]["id"]
                temp["num"] = sell_item_config[weight_id]["num"]
                cost = sell_item_config[weight_id]["cost"]
                cost_type = "diamond"
                temp["type"] = "item"
            #打折
            special_config = shop_extra_config["special"]
            special_num = utils.get_item_by_random_simple(special_config.items())
            cost = int(cost * float(special_num))
            temp["cost"] = cost
            temp["special_num"] = special_num
            temp["cost_type"] = cost_type
            result[str(i)] = temp
        self.common_shop = result
        self.put()
        return result
            
    def __weight_back(self,weight_dict):    
        back = utils.get_item_by_random_simple(weight_dict.items())
        return back
    
    def __main_install(self, eid, lv):
        result = {}
        equipment_config = game_config.equipment_config[eid]
        _type = equipment_config['type']
        category = equipment_config['category']
        init_main_attr = equipment_config["effect"]
        init_main_attr_grow = equipment_config["effect_growth"]

        if _type == "mainWeap":
            result["minDamage"] = int(init_main_attr[0] + init_main_attr_grow[0] * (lv - 1))
            result["maxDamage"] = int(init_main_attr[1] + init_main_attr_grow[1] * (lv - 1))
        else:
            if _type == "secWeap":
                second_equip_config = game_config.vice_attr_config['secWeap_' + category]
            else:
                second_equip_config = game_config.vice_attr_config[_type]
            main_attr = second_equip_config['main_trait']
            result[main_attr] = int(init_main_attr[0] + init_main_attr_grow[0] * (lv - 1))
        return result