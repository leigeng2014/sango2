#-*- coding: utf-8 -*-
import copy
from apps.oclib.model import UserModel
from apps.models.user_equipments import UserEquipments
from apps.config import game_config
from apps.models.virtual.card import Card as CardMod

class UserCards(UserModel):  
    pk = 'uid'
    fields = ['uid','cid','skill_offensive','skill_defensive','equipments']      
    def __init__(self,uid = None):
        """用户主角色的基本信息
        """
        self.uid = uid
        self.cid = ''
        self.skill_offensive = [] #作战技能(用作作战)
        self.skill_defensive = [] #竞技技能(用于竞技)
        self.equipments = {
            'mainWeap':'',  #01主手武器
            'secWeap':'',   #02副手武器
            'helmet':'',    #03头盔
            'necklace':'',  #04项链
            'armor':'',     #05胸甲
            'belt':'',      #06腰带
            'glove':'',     #07手套
            'amulet':'',    #08手腕(戒子)
            'pants':'',     #09裤子(护腿)
            'shoes':'',     #10鞋子
        }

    @classmethod
    def get_instance(cls,uid):
        obj = super(UserCards,cls).get(uid)        
        if obj is None:
            obj = cls._install(uid)
        return obj
    
    @classmethod
    def get(cls,uid):
        obj = super(UserCards,cls).get(uid)
        return obj
    
    @classmethod
    def _install(cls,uid):
        obj = cls(uid)
        obj.put()
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    @property
    def force(self):
        """我的战斗力
        """
        cardmod = self.card_obj()
        result = cardmod.maxDamage + cardmod.physDef + cardmod.magDef + \
            cardmod.critical + cardmod.intelligence + cardmod.durability + \
            int(cardmod.invasion * 5 / 3) + (cardmod.evasion * 5) + int((cardmod.hp + cardmod.mp)/10) 
        return result     
    
    @property
    def category(self):
        """主角色类型
        """
        card_config = game_config.card_config
        return card_config[self.cid]["category"]
 
    def card_obj(self):
        """获取角色的信息
        """
        #获取主将的mod对象 
        lv = self.user_base.property_info.property_info["lv"]
        cardmod = CardMod.get(self.cid,lv,equip_attr = self.get_equip_attr()) 
        return cardmod
        
    def get_equip_attr(self):
        """获取装备的属性,ctype:'0'代表角色，'1','2','3'代表佣兵
        """
        attr_list = {'vitality':0,'strength':0,'stealth':0,'intelligence':0,'hp':0,\
            'physDef':0,'magDef':0,'durability':0,'mp':0,'mpRecover':0,'critical':0,\
            'invasion':0,'evasion':0,'minDamage':0,'maxDamage':0}
        user_equipments_obj = UserEquipments.get_instance(self.uid)
        equipments = user_equipments_obj.equipments
        
        #用户身上的装备信息        
        user_equipments = self.equipments.values()
        strengthen_config  = game_config.equipment_strengthen_config    
        class_influence = strengthen_config["class_influence"]  
        effect_base = strengthen_config["effect_base"] 
          
        material_config = game_config.material_config   
        gem_config = game_config.gem_config["gem_upgrade"] 
        for equip in user_equipments:
            if equip and (equip in equipments):
                equip_dict = copy.deepcopy(equipments[equip])
                quality = equip_dict["quality"]
                minilv = equip_dict["minilv"]
                main_attr = equip_dict['main_attr'] 
                vice_attr = equip_dict['vice_attr']
                #把主属性加到attr_list,并加上强化的效果
                for k,v in main_attr.items():
                    if minilv > 0:    
                        #强化公式                 
                        main_attr_effect = int(v * effect_base[str(minilv)] / 100 * class_influence[str(quality)]["effect_multiplier"])
                        main_attr = main_attr_effect + v
                        attr_list[k] += main_attr
                    else:
                        attr_list[k] += int(v)  
                        
                #把副属性加到attr_list
                for k_,v_ in vice_attr.items():
                    attr_list[k_] += int(v_)
                #把镶嵌的宝石的属性加到attr_list                
                for _,_v in equip_dict["gem_hole"].items():
                    if _v not in [0,1]:
                        item_config = material_config[_v]
                        gem_effect = item_config['gem_effect']
                        gem_lv = item_config['lv']
                        effect = gem_config[str(gem_lv)]['effect']
                        attr_list[gem_effect] += int(effect)
        return attr_list