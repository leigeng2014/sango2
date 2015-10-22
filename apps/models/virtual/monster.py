#-*- coding: utf-8 -*-
from apps.config import game_config

class Monster(object):
    @classmethod    
    def get(cls,mid):
        """根据怪物mid获取信息
        """        
        obj = cls()
        monster_detail = game_config.monster_config[mid]
        obj.mid = mid
        obj.lv = monster_detail.get('lv')
        obj.vitality = monster_detail.get('vitality')      #耐力
        obj.strength = monster_detail.get('strength')      #力量
        obj.stealth = monster_detail.get('stealth')       #敏捷
        obj.intelligence = monster_detail.get('intelligence')  #智力
        obj.hp = monster_detail.get('hp')            #hp  

        obj.physDef = monster_detail.get('physDef')       #物抗
        obj.magDef = monster_detail.get('magDef')        #魔抗
        obj.durability = monster_detail.get('durability')    #韧性
        obj.mp = monster_detail.get('mp')            #mp
        obj.mpRecover = monster_detail.get('mpRecover')     #mp回复力
        obj.critical = monster_detail.get('critical')      #暴击 
        obj.invasion = monster_detail.get('invasion')      #命中
        obj.evasion = monster_detail.get('evasion')       #闪避
        obj.minDamage = monster_detail.get('minDamage')     #最小伤害
        obj.maxDamage = monster_detail.get('maxDamage')     #最大伤害
        obj.skill_list = monster_detail.get('skill',[])
        return obj
    
    @classmethod
    def get_compete(cls,attr_dict = {}):
        obj = cls()
        #主属性
        obj.mid = attr_dict.get("cid")
        obj.lv = attr_dict.get("lv")
        obj.vitality = int(attr_dict.get("vitality",0))    #耐力
        obj.strength = int(attr_dict.get("strength",0))
        obj.stealth = int(attr_dict.get("stealth",0)) #敏捷
        obj.intelligence = int(attr_dict.get("intelligence",0))#智力
        
        #战斗属性
        obj.hp = int(attr_dict.get("hp",0))           #hp 
        obj.physDef = int(attr_dict.get("physDef",0))#物抗
        obj.magDef = int(attr_dict.get("magDef",0))#魔抗
        obj.durability = int(attr_dict.get("durability",0))#韧性
        obj.mp = int(attr_dict.get("mp",0))          #mp
        obj.mpRecover = int(attr_dict.get("mpRecover",0))#mp回复力
        obj.critical = int(attr_dict.get("critical",0))#暴击 
        obj.invasion = int(attr_dict.get("invasion",0))#命中
        obj.evasion = int(attr_dict.get("evasion",0))#闪避 
        obj.minDamage = int(attr_dict.get("minDamage",0))    #最小伤害
        obj.maxDamage = int(attr_dict.get("maxDamage",0))    #最大伤害
       
        #技能信息
        obj.skill_list = attr_dict["skill_list"]
        return obj