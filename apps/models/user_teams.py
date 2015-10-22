#-*- coding: utf-8 -*-
import copy
from apps.oclib.model import UserModel
from apps.config import game_config

class UserTeams(UserModel):  
    pk = 'uid'
    fields = ['uid','team','develop_last','develop_info','teams_info']  
    def __init__(self):
        """用户佣兵基本信息
        """
        self.uid = ''
        self.team = []           #出站中的佣兵列表（现版本为1个）
        #佣兵培养信息
        self.develop_info = {}   
        #存储培养临时信息
        self.develop_last = {'vitality':0,'strength':0,'stealth':0,'intelligence':0} 
        #佣兵信息
        self.teams_info = {}


    @classmethod
    def get_instance(cls,uid):
        obj = super(UserTeams,cls).get(uid)        
        if obj is None:
            obj = cls._install(uid)
        return obj
    
    @classmethod
    def get(cls,uid):
        obj = super(UserTeams,cls).get(uid)
        return obj
    
    @classmethod
    def _install(cls,uid):
        obj = cls()
        obj.uid = uid
        obj.put()
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    def add_team(self,tid):
        """开放佣兵，tid = 1/2/3
        """
        from apps.models.user_cards import UserCards        
        from apps.models.virtual.card import Card as CardMod
        user_cards_obj = UserCards.get(self.uid)
        card_mod = CardMod(user_cards_obj.cid)
        card_teams = card_mod.teams #获取佣兵的信息
        tcid = card_teams[str(tid)]  
        card_config = game_config.card_config[tcid]      
        self.teams_info[str(tid)] = {
                'cid':tcid,
                'equipments':{
                    'mainWeap':'',  #01主手武器
                    'secWeap':'',   #02副手武器   
                    'armor':'',     #05胸甲     
                    'pants':'',     #09裤子
                },   
                'refresh_num':0,
                'skill_list':{'1':{"skill":card_config["skill"][0],"is_lock":0}},             
        }
        self.develop_info[str(tid)] = {'vitality':0,'strength':0,'stealth':0,'intelligence':0}
        self.put()

    def card_obj(self,tid):
        """获取佣兵的信息
        """
        #获取主将的mod对象 
        from apps.models.virtual.card import Card as CardMod
        lv = self.user_base.property_info.property_info["lv"]
        tcid = self.teams_info[str(tid)]["cid"]
        cardmod = CardMod.get(tcid,lv,equip_attr = self.get_equip_attr(str(tid)))
        return cardmod
    
    def category(self,tid):
        """主角色类型
        """
        card_config = game_config.card_config
        return card_config[self.teams_info[tid]["cid"]]["category"]
        
    def get_equip_attr(self,tid):
        """获取装备的属性,ctype:'1','2','3'代表佣兵
        """
        attr_list = {'vitality':0,'strength':0,'stealth':0,'intelligence':0,'hp':0,\
            'physDef':0,'magDef':0,'durability':0,'mp':0,'mpRecover':0,'critical':0,\
            'invasion':0,'evasion':0,'minDamage':0,'maxDamage':0}
        from apps.models.user_equipments import UserEquipments        
        user_equipments_obj = UserEquipments.get_instance(self.uid)
        equipments = user_equipments_obj.equipments
        
        #佣兵身上的装备信息
        user_equipments = self.teams_info[str(tid)]["equipments"].values()
        #佣兵培养的信息
        develop_info = self.develop_info.get(str(tid),{})
            
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
                        main_attr_effect = int(v * effect_base[str(minilv)] / 100 * class_influence[str(quality)]["effect_multiplier"])
                        main_attr = main_attr_effect + v
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
                        
        attr_list["vitality"] += develop_info.get("vitality",0)
        attr_list["strength"] += develop_info.get("strength",0)
        attr_list["stealth"] += develop_info.get("stealth",0)
        attr_list["intelligence"] += develop_info.get("intelligence",0)
        return attr_list