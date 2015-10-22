#-*- coding: utf-8 -*-
import copy
import random

from apps.common import utils
from apps.config import game_config
from apps.oclib.model import UserModel
from apps.models.user_property import UserProperty

class UserEquipments(UserModel):
    """用户装备信息
    """
    pk = 'uid'
    fields = ['uid', 'equipments','equip_settings']

    def __init__(self,uid=None):
        self.uid = uid
        self.equipments = {}
        self.equip_settings = []
        
    @classmethod
    def get_instance(cls,uid):
        obj = super(UserEquipments,cls).get(uid)
        if not obj:
            obj = cls.create(uid)    
            obj.put()        
        return obj    
    
    @classmethod
    def get(cls,uid):
        obj = super(UserEquipments,cls).get(uid)
        return obj
    
    @classmethod    
    def create(cls,uid):
        obj = cls()
        obj.uid = uid 
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base

    def add_equipment(self, eid, quality,hole='',special_num = '',add_type="dungeon"):
        """加装备       
        :param eid:str 装备id
        :param lv:int  装备id
        :param quality:int 装备品质
        :param add_type:str   添加来源
        :return:   
        """
        eqdbid = utils.create_gen_id()
        equipment = {}
        equipment["eid"]        = eid
        equipment["lv"]         = game_config.equipment_config[eid]["lv"]
        equipment["quality"]    = quality
        equipment["minilv"]     = 0
        equipment["strenth_cast"] = ("0", 0)     #强化已经消耗的资源，逆向运算比较繁琐
        equipment["star"] = 0
        equipment["main_attr"] = self.__main_install(eid, equipment["lv"])
        equipment["vice_attr"]  = self.__vice_install(eid, equipment["lv"], quality)
        equipment["gem_hole"] = self.__gem_install(equipment["lv"], quality,hole)
        equipment["special_attr"] = self.__special_install(game_config.equipment_config[eid]["type"],equipment["lv"],quality,special_num)
        copy_equipment = copy.deepcopy(equipment)

        #如果是战场掉落的,检查装备是否可以卖掉
        coin = 0  
        flag = False
        if add_type == "dungeon":
            #检查其他职业的是否需要卖掉
            if 0 in self.equip_settings:
                category = game_config.equipment_config[eid]["category"]
                from apps.models.user_cards import UserCards
                user_cards_obj = UserCards.get(self.uid)
                user_category = user_cards_obj.category
                if int(user_category) != int(category):
                    flag = True  
                                    
            #检查对应品质的是否需要卖掉                            
            elif quality in self.equip_settings:
                flag = True 
                              
            #检查背包是否满，满的话需要卖掉    
            if not flag:
                user_property_obj = UserProperty.get(self.uid)
                max_card_num = user_property_obj.property_info["max_card_num"]
                if max_card_num <= self.my_card_num:  
                    flag = True 
            
            if flag:             
                coin = self.__calculate_value(eqdbid, equipment)
                self.user_base.property_info.add_coin(coin)
            else:
                self.equipments.update({eqdbid: equipment})
                self.put()            
        else:
            self.equipments.update({eqdbid: equipment})
            self.put()

        copy_equipment["coin"] = coin      
        return eqdbid, copy_equipment

    def put_on(self, eqdbid, part,cid):
        """穿装备
        """
        equipment = self.equipments.get(eqdbid)
        if equipment: 
            if cid == '0':
                from apps.models.user_cards import UserCards
                user_cards_obj = UserCards.get(self.uid)
                user_cards_obj.equipments[part] = eqdbid                
                user_cards_obj.put()
            else:
                from apps.models.user_teams import UserTeams
                user_teams_obj = UserTeams.get(self.uid)
                user_teams_obj.teams_info[cid]["equipments"][part] = eqdbid
                user_teams_obj.put() 
            self.put()
        from apps.models.rank import update_force_rank
        update_force_rank(self.uid)
        return True
    
    def take_off(self, eqdbid,part,cid):
        """脱掉装备
        """
        equipment = self.equipments.get(eqdbid, False)
        if equipment:
            if cid == '0':
                from apps.models.user_cards import UserCards
                user_cards_obj = UserCards.get(self.uid)
                user_cards_obj.equipments[part] = ''
                user_cards_obj.put()
            else:
                from apps.models.user_teams import UserTeams
                user_teams_obj = UserTeams.get(self.uid)
                user_teams_obj.teams_info[cid]["equipments"][part] = ''
                user_teams_obj.put()
            self.put()
        from apps.models.rank import update_force_rank
        update_force_rank(self.uid)
        return True
    
    @property
    def my_card_num(self):
        """背包中装备的个数，除去身上穿的
        """
        return len(self.equipments) - len(self.get_puton_equip())   
     
    def single_sell(self, eqdbid):
        """卖掉装备
        """
        if not eqdbid in self.equipments:
            return 0
        if self.is_embed(eqdbid):
            return 0
        if eqdbid in self.get_puton_equip():
            return 0
        equipment = self.equipments[eqdbid]
        money = self.__calculate_value(eqdbid, equipment)
        property_obj = UserProperty.get(self.uid)
        property_obj.add_coin(money)
        self.equipments.pop(eqdbid)
        self.put()
        return money

    def batch_sell(self, quality):
        """根据品质卖装备
        """
        money = 0
        puton_equip = self.get_puton_equip()
        for k, v in self.equipments.items():
            if k in puton_equip:
                continue
            if self.is_embed(k):
                continue
            if v["quality"] == quality:
                money += self.__calculate_value(k, v)
                self.equipments.pop(k)
        self.put()
        property_obj = UserProperty.get(self.uid)
        property_obj.add_coin(money)
        return money

    def __main_install(self, eid, lv):
        """主属性
        """
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
        '''副属性
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

    def __special_install(self,equip_type,lv,quality,special_num):
        """神器属性
        """
        result = {}
        if quality < 5:
            return {}
        
        if special_num != '' and (not utils.is_happen(0.05)):
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
    
    def __weight_back(self, _dic, pop=True):
        """默认做弹出元素的操作
        """
        back = utils.get_item_by_random_simple(_dic.items())
        if pop:
            _dic.pop(back)
        return back

    def __calculate_value(self, eqdbid, equipment):  
        """计算装备卖掉的coin
        """      
        eid = equipment["eid"]
        lv = equipment["lv"]
        quality = equipment["quality"]
        cfg = game_config.equipment_config
        sell = cfg[eid]["sell"]
        sell_growth = cfg[eid]["sell_growth"]
        money = sell + (lv - 1) * sell_growth
        class_influence = game_config.equipment_strengthen_config["class_influence"]
        sell_multiplier = class_influence[str(quality)]["sell_multiplier"]
        return int(money * sell_multiplier)
    
    def is_embed(self,eqdbid):
        """检查装备是否镶嵌宝石
        """
        flag = False
        equipment = self.equipments[eqdbid]
        for hole in equipment["gem_hole"].values():
            if hole not in [0,1]:
                flag = True
                break
        return flag
    
    def get_puton_equip(self):
        """获取已经穿的装备
        """
        from apps.models.user_cards import UserCards
        from apps.models.user_teams import UserTeams
        equipments = []
        user_cards_obj = UserCards.get(self.uid)
        for equip in user_cards_obj.equipments:
            if user_cards_obj.equipments[equip]:
                equipments.append(user_cards_obj.equipments[equip])
                
        user_teams_obj = UserTeams.get_instance(self.uid)
        for _,v in user_teams_obj.teams_info.items():
            for equip in v["equipments"]:
                if v["equipments"][equip]:
                    equipments.append(v["equipments"][equip])        
        return equipments
    
    def open_gem(self,eqdbid,num):
        """装备宝石洞开启，{0:0,1:0,2:0,3:0}键代表宝石洞的变好,值0未开启,1开启,其他值宝石Id
        :param eqdbid 装备id
        :param num:int  孔的个数
        """
        equipment = self.equipments[eqdbid]
        temp = {}
        for i in range(4):
            temp[i] = 0
            if i < num:
                temp[i] = 1
        equipment["gem_hole"] = temp
        self.put()
        return equipment
    
    def get_special_devour_exp(self,eqdbid):
        """神器被吞噬提供的经验
        """
        exp = 0
        equipment = self.equipments[eqdbid]
        special_attr_list = equipment["special_attr"]
        special_attr_config = game_config.special_attr_config
        for _,v in special_attr_list.items():
            exp += int(special_attr_config[v["id"]]["exp"])
        return exp
    
    def add_special_exp(self,eqdbid,add_exp):
        """给神器属性加经验
        """
        equipment = self.equipments[eqdbid]
        special_attr = equipment["special_attr"]
        for k,v in special_attr.items():
            star,_exp = self.__add_special_exp(v["star"],v["exp"],add_exp)
            special_attr[k]["star"] = star
            special_attr[k]["exp"] = _exp
        self.put()
        return equipment
    
    def __add_special_exp(self,star,exp,add_exp):
        """给神器属性加经验
        """
        special_attr_star_config = game_config.special_attr_level_config
        max_star = max([int(i) for i in special_attr_star_config["exp"].keys()])
        new_star = star
        new_exp = exp + add_exp
        if new_exp >= special_attr_star_config["exp"][str(max_star)]:
            new_exp = special_attr_star_config["exp"][str(max_star)]
            new_star = max_star
        else: 
            for next_star in range(star+1,max_star+1):
                next_star_exp = special_attr_star_config["exp"][str(next_star)]
                if new_exp >= next_star_exp:
                    new_star = next_star
                else:
                    break
        return new_star,new_exp