#-*- coding: utf-8 -*-
import copy
from apps.config import game_config
        
class Card(object):
    """角色和佣兵模型，耐力，力量，敏捷，智力，为基础属性，其他的为战斗属性
    """
    def __init__(self,cid,lv=1,subarea='1'):
        self.lv = lv
        self.cid = cid
        self.subarea = subarea
        self.card_detail = copy.deepcopy(game_config.card_config[cid])
        self.card_category_config = copy.deepcopy(game_config.card_category_config[self.card_detail['category']])
       
    @classmethod
    def get(cls,cid,lv=1,equip_attr = {},subarea='1'):
        obj = cls(cid,lv=lv,subarea = subarea)
        #主属性
        obj.vitality = int(obj.card_detail.get('vitality',0) + (lv -1)* obj.card_detail.get('vitality_growth',0) + equip_attr.get('vitality',0))     #耐力
        obj.strength = int(obj.card_detail.get('strength',0) + (lv -1)* obj.card_detail.get('strength_growth',0) + equip_attr.get('strength',0))     #力量
        obj.stealth = int(obj.card_detail.get('stealth',0) + (lv -1)* obj.card_detail.get('stealth_growth',0) + equip_attr.get('stealth',0))     #敏捷
        obj.intelligence = int(obj.card_detail.get('intelligence',0) + (lv -1)* obj.card_detail.get('intelligence_growth',0) + equip_attr.get('intelligence',0))#智力
        
        #战斗属性
        obj.hp = int(obj.card_detail.get('hp',0) + (lv -1)* obj.card_detail.get('hp_growth',0) + obj.vitality*10 + equip_attr.get('hp',0))           #hp 
        obj.physDef = int(obj.card_detail.get('physDef',0) + (lv -1)* obj.card_detail.get('physDef_growth',0) + obj.strength + equip_attr.get('physDef',0))     #物抗
        obj.magDef = int(obj.card_detail.get('magDef',0) + (lv -1)* obj.card_detail.get('magDef_growth',0) + obj.intelligence + equip_attr.get('magDef',0))      #魔抗
        obj.durability = int(obj.card_detail.get('durability',0) + (lv -1)* obj.card_detail.get('durability_growth',0) + obj.vitality + equip_attr.get('durability',0)) #韧性
        obj.mp = int(obj.card_detail.get('mp',0) + (lv -1)* obj.card_detail.get('mp_growth',0) + equip_attr.get('mp',0))          #mp
        obj.mpRecover = int(obj.card_detail.get('mp_recover',0) + 0.0188*obj.intelligence + equip_attr.get('mpRecover',0))    #mp回复力
        obj.critical = int(obj.card_detail.get('critical',0) + (lv -1)* obj.card_detail.get('critical_growth',0) + obj.stealth + equip_attr.get('critical',0))      #暴击 
        obj.invasion = int(obj.card_detail.get('invasion',0) + (lv -1)* obj.card_detail.get('invasion_growth',0) + obj.strength*0.6 + equip_attr.get('invasion',0))     #命中
        obj.evasion = int(obj.card_detail.get('evasion',0) + (lv -1)* obj.card_detail.get('evasion_growth',0) + 0.2*obj.stealth + equip_attr.get('evasion',0))        #闪避
        
        main_attr = obj.card_category_config["main_attr"]
        #不同类型的职业，伤害的初始值跟主属性有关
        if main_attr == "strength":
            obj.minDamage = int(obj.strength / 2 + equip_attr.get('minDamage',0))      #最小伤害
            obj.maxDamage = int(obj.strength  + equip_attr.get('maxDamage',0))         #最大伤害
        elif main_attr == "stealth":
            obj.minDamage = int(obj.stealth / 2 + equip_attr.get('minDamage',0))       #最小伤害
            obj.maxDamage = int(obj.stealth  + equip_attr.get('maxDamage',0))          #最大伤害
            
        elif main_attr == "intelligence":
            obj.minDamage = int(obj.intelligence / 2 + equip_attr.get('minDamage',0))      #最小伤害
            obj.maxDamage = int(obj.intelligence  + equip_attr.get('maxDamage',0))    #最大伤害
        #技能信息，如果是主角色，此信息为全部技能，战斗时需要读取作战的技能信息
        obj.skill_list = game_config.card_config[cid]['skill']
        return obj
    
    @property
    def teams(self):
        """佣兵信息，如果是佣兵，则佣兵信息为空
        """
        card_category_config = game_config.card_category_config[self.card_detail.get('category')]
        return card_category_config['team']