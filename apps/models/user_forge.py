#-*- coding: utf-8 -*-
import time
import copy
import random
from apps.common import utils
from apps.oclib.model import UserModel
from apps.config import game_config

class UserForge(UserModel):
    """用户打造装备
    """
    pk = 'uid'
    fields = ['uid', 'free_times','cost_smelting','refresh_date','equipments','special_equipments','special_equip_lv']

    def __init__(self,uid=None):
        self.uid = uid
        self.free_times = 0
        self.cost_smelting = 0
        self.equipments = {}   
        self.refresh_date = int(time.time()) 
        self.special_equipments = {} 
        self.special_equip_lv = 1   
        
    @classmethod
    def get_instance(cls,uid):
        obj = super(UserForge,cls).get(uid)
        if not obj:
            obj = cls._install(uid)
        return obj    
    
    @classmethod
    def get(cls,uid):
        obj = super(UserForge,cls).get(uid)
        return obj
    
    @classmethod
    def _install(cls,uid):
        obj = cls()
        obj.uid = uid
        obj.free_times = 2   
        cost,eqdbid,equipment = obj.forge()
        obj.equipments = {eqdbid:equipment}     
        obj.need_smelting = cost
        obj.put()
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    def forge(self):
        """打造装备
        """
        forge_config = game_config.equipment_forge_config 
        class_influence = forge_config["common_forge"]["class_influence"] 
        lv = forge_config["common_forge"]["lv"] 
        #获取装备的品质
        equip_quality = utils.get_item_by_random_simple([(k,v["weight"]) for k,v in class_influence.items()])
        cost = class_influence[equip_quality]["cost"]#装备的所需要的熔炼值
        #获取装备的等级
        lv_flag = utils.get_item_by_random_simple([(k,v) for k,v in lv.items()])
        user_lv = self.user_base.property_info.property_info["lv"]
        if lv_flag == "add_weight":
            level = ((user_lv-1) / 5) + 1
        else:
            level = (user_lv-1) / 5
            if level == 0:
                level =1
                
        equip_lv = level * 5
        equipment_lv_config = game_config.equipment_lv_config
        eid = utils.random_choice(equipment_lv_config[str(equip_lv)],1)[0]
        #生成打造装备
        eqdbid,equipment = self.__add_equipment(eid,int(equip_quality))
        self.equipments = {eqdbid: equipment}
        self.cost_smelting = cost
        self.put()
        return cost,eqdbid,equipment
    
    def special_forge(self):
        """神器打造列表
        """
        result = {}        
        user_lv = self.user_base.property_info.lv
        equip_lv = (user_lv / 5) * 5  if (user_lv / 5) * 5 else 1 
        from apps.models.user_cards import UserCards    
        user_cards_obj = UserCards.get(self.uid)
        category = user_cards_obj.category
        equip_list = copy.deepcopy(game_config.equipment_lv_config[str(equip_lv)])
        i = 0
        for eid in equip_list:
            equip_config = game_config.equipment_config[eid]
            if equip_config["type"] in ["mainWeap",'secWeap'] and category != equip_config["category"]: 
                continue 
            i += 1
            _,equipment = self.__add_equipment(eid,5,special_num=1)
            result[str(i)] = equipment
            
        for eid in equip_list:
            equip_config = game_config.equipment_config[eid]
            if equip_config["type"] in ["mainWeap",'secWeap'] and category != equip_config["category"]: 
                continue   
            i += 1
            _,equipment = self.__add_equipment(eid,5,special_num=2)
            result[str(i)] = equipment
            
        self.special_equipments = result
        self.special_equip_lv = equip_lv
        self.put()
        return True    
    
    def __add_equipment(self, eid,quality,hole='',special_num = ''):
        '''生成锻造装备
        @param eid:str
        @param quality:int
        '''
        eqdbid = utils.create_gen_id()
        equipment = {}
        equipment["eid"] = eid
        equipment["lv"] = game_config.equipment_config[eid]["lv"]
        equipment["quality"] = quality
        equipment["minilv"] = 0        
        equipment["strenth_cast"] = ("0", 0)
        equipment["star"] = 0
        equipment["main_attr"] = self.__main_install(eid, equipment["lv"])
        equipment["vice_attr"] = self.__vice_install(eid, equipment["lv"], quality)
        equipment["special_attr"] = self.__special_install(game_config.equipment_config[eid]["type"],equipment["lv"],quality,special_num)
        equipment["gem_hole"] = self.__gem_install(equipment["lv"], quality,hole)
        return eqdbid, equipment

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

    def __vice_install(self, eid, lv, quality):
        '''
        :param quality:
        '''
        cfg = game_config.equipment_config
        category = cfg[eid]['category']
        tmp_key = cfg[eid]['type']
        if quality == 1:
            return {}
        
        if category != '0':
            tmp_key = tmp_key + '_' + category
    
        vice_cfg = game_config.vice_attr_config[tmp_key]
        trait_weight =  copy.deepcopy(vice_cfg['trait_weight'])
        trait_effect = vice_cfg['trait_effect']        
        result = {}
        for _ in range(quality-1):
            attr =  utils.get_item_by_random_simple(trait_weight.items()) 
            trait_weight.pop(attr)          
            inner_cfg = trait_effect[str(quality)][attr]
            fixed = inner_cfg["effect"] + inner_cfg["effect_growth"] * (lv - 1)
            min_value = int(fixed * (1 - inner_cfg["variance"]))
            max_value = int(fixed * (1 + inner_cfg["variance"])) 
            if min_value < 1:
                min_value = 1
            if max_value < 1:
                max_value = 1                           
            value = random.randint(min_value, max_value)
            if (value > fixed) and (value - fixed > 50):
                value = fixed + 50                
            elif (value < fixed) and (fixed - value > 50):
                value = fixed - 50 
            result[attr] = int(value)
        return result
    
#     def __gem_install(self, lv, quality):
#         """装备宝石洞开启，{0:0,1:0,2:0,3:0}键代表宝石洞的变好,值0未开启,1开启,其他值宝石Id
#         """
#         result = {}
#         for x in range(4):
#             result[x] = 0
#         cfg = game_config.equipment_drop_config
#         hole_num = cfg["hole_num"]
#         back_key = utils.get_item_by_random_simple(hole_num.items())
#         for x in range(int(back_key)):
#             result[x] = 1
#         return result
    def __gem_install(self, lv, quality,hole):
        """装备宝石洞开启，{0:0,1:0,2:0,3:0}键代表宝石洞的变好,值0未开启,1开启,其他值宝石Id
        """
        if hole == "":
            drop_config = game_config.equipment_drop_config
            hole_num = drop_config["hole_num"]
            num = int(utils.get_item_by_random_simple(hole_num.items()))
        else:
            num = int(hole)
            
        result = {}
        for i in range(4):
            result[i] = 0
            if i < num:
                result[i] = 1
        return result
      
    def __special_install(self,equip_type,lv,quality,special_num):
        """神器属性
        """
        result = {}
        if quality < 5:
            return {}
        
        if special_num == '' and (not utils.is_happen(0.05)):
            return {}
        
        special_attr_config = game_config.special_attr_config
        #获取装备类型对应的神器属性列表
        ############此处以后需要优化################
        special_equip_config = {}
        for k,v in special_attr_config.items():
            if v["equip_type"][0] not in special_equip_config:            
                special_equip_config[v["equip_type"][0]] = [k]
            else:
                special_equip_config[v["equip_type"][0]].append(k)
        ##############################
        special_attr_list = utils.random_choice(special_equip_config[equip_type],special_num)
        i = 0
        for spid in special_attr_list:
            i += 1
            result[str(i)] = {"id":spid,"star":1,"exp":0}
        return result