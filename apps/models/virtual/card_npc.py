#-*- coding: utf-8 -*-
import copy
from apps.config import game_config
        
class CardNpc(object):
    """角色和佣兵模型，耐力，力量，敏捷，智力，为基础属性，其他的为战斗属性
    """
    def __init__(self,cid,lv=1,subarea='1'):
        self.lv = lv
        self.cid = cid
        self.subarea = subarea
        self.card_detail = copy.deepcopy(game_config.card_config[cid])
        self.card_category_config = copy.deepcopy(game_config.card_category_config[self.card_detail['category']])
       
    @classmethod
    def get(cls,cid,lv=1,attr_dict = {},subarea='1'):
        obj = cls(cid,lv=lv,subarea = subarea)
        #主属性
        obj.vitality = int(attr_dict.get("vitality",0) + attr_dict.get("vitality_growth",0))    #耐力
        obj.strength = attr_dict.get("strength",0) + attr_dict.get("strength_growth",0)
        obj.stealth = attr_dict.get("stealth",0) + attr_dict.get("stealth_growth",0)  #敏捷
        obj.intelligence = attr_dict.get("intelligence",0) + attr_dict.get("intelligence_growth",0)#智力
        
        #战斗属性
        obj.hp = int(attr_dict.get("hp",0) + attr_dict.get("hp_growth",0) + obj.vitality*10)           #hp 
        obj.physDef = int(attr_dict.get("physDef",0) + attr_dict.get("physDef_growth",0) + obj.strength)#物抗
        obj.magDef = int(attr_dict.get("magDef",0)+ attr_dict.get("magDef_growth",0) + obj.intelligence)#魔抗
        obj.durability = int(attr_dict.get("durability",0)+ attr_dict.get("durability_growth",0) + obj.vitality)#韧性
        obj.mp = int(attr_dict.get("mp",0)+ attr_dict.get("mp_growth",0))          #mp
        obj.mpRecover = int(attr_dict.get("mp_recover",0) + 0.0188*obj.intelligence)#mp回复力
        obj.critical = int(attr_dict.get("critical",0)+ attr_dict.get("critical_growth",0) + obj.stealth)#暴击 
        obj.invasion = int(attr_dict.get("invasion",0)+ attr_dict.get("invasion_growth",0) + obj.strength*0.6)#命中
        obj.evasion = int(attr_dict.get("evasion",0)+ attr_dict.get("evasion_growth",0) + 0.2*obj.stealth)#闪避       
        main_attr = obj.card_category_config["main_attr"]
        #不同类型的职业，伤害的初始值跟主属性有关
        if main_attr == "strength":
            obj.minDamage = int(obj.strength / 2)    #最小伤害
            obj.maxDamage = int(obj.strength)        #最大伤害
        elif main_attr == "stealth":
            obj.minDamage = int(obj.stealth / 2)      #最小伤害
            obj.maxDamage = int(obj.stealth)          #最大伤害
            
        elif main_attr == "intelligence":
            obj.minDamage = int(obj.intelligence / 2)  #最小伤害
            obj.maxDamage = int(obj.intelligence)      #最大伤害
        #技能信息
        obj.skill_list = attr_dict["skill"]
        obj.force = obj.maxDamage + obj.physDef + obj.magDef + \
            obj.critical + obj.intelligence + int(obj.invasion * 5 / 3) + \
            (obj.evasion * 5) + int((obj.hp + obj.mp)/10)
        return obj