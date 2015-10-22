#-*- coding: utf-8 -*-
import random
from apps.common import utils
from apps.models.virtual.skill import Skill

class Soldier(object):
    def __init__(self,dungeon_obj,card_obj):
        self.card = card_obj     #自己的信息
        self.dun = dungeon_obj   #战场信息       
        ########战斗属性#######
        self.critical_rate = self.card.critical / (0.5 + self.card.lv * 1.5) #暴击率
        self.durability_rate = self.card.durability / (1.2 + self.card.lv * 3.6) #抗暴率
        self.evasion_rate = self.card.evasion / (0.13 + self.card.lv * 0.4)  #闪避率
        self.invasion_rate = self.card.invasion / (0.6 + self.card.lv * 1.8) #命中率 
        self.physDef = self.card.physDef /((0.5 + self.card.lv * 1.5) * 100) #物理防御能力
        self.magDef = self.card.magDef /((0.5 + self.card.lv * 1.5) * 100)   #魔法防御能力
        self.mp = self.max_hp = self.card.hp
        self.hp = self.max_mp = self.card.mp
        #技能对象列表 
        self.skill_obj_list = [Skill(self,skill) for skill in self.card.skill_list if skill]
        self.buff_list = {}                  #自身的buff（如攻击加强，防御加强,）
        self.current_skill_index = 0         #技能循环释放时记录当前索引
        self.skill_interval_time = 2         #下一轮技能释放的间隔数
    
    @property    
    def our_army(self):
        if self.position.startswith('1_'):
            return self.dun.first_army
        return self.dun.second_army
    
    @property
    def enemy_army(self):
        if self.position.startswith('1_'):
            return self.dun.second_army
        return self.dun.first_army
                        
    def action(self):
        """
                攻击的时候，先把自己身上的人的技能顺序执行，然后2次普通攻击后,再释放技能
                如果释放技能的时候mp不足,此次攻击就用普通攻击代替。
        """
        self.load_buff()
        if self.current_skill_index <= len(self.skill_obj_list) - 1:  
            current_skill_obj = self.skill_obj_list[self.current_skill_index]
            if self.card.mp < current_skill_obj.mp:
                self.common_attack();
            else:                 
                current_skill_obj.start()
        else:
            self.common_attack();

        self.current_skill_index += 1 
        if (self.current_skill_index - len(self.skill_obj_list) >= self.skill_interval_time - 1):
            self.current_skill_index = 0

    def add_buff(self, buff):
        """添加buff
        """
        self.buff_list.append(buff)
        
    def load_buff(self):
        """攻击时检查自己的buff
        """
        pass
        
    def common_attack(self):
        """普通攻击
        """                       
        if self.position.startswith('1_'): 
            target = utils.random_choice(self.enemy_army,1)[0]
        else:
            target = utils.random_choice(self.our_army,1)[0]
        dmg = random.randint(int(self.card.minDamage),int(self.card.maxDamage))    
        final_dmg,is_miss,is_crit = self.__get_final_dmg(self,target,dmg,dmg_type='phys')
        target.card.hp -= final_dmg
        result = {'unit':self.position,'type':'common','effects':[],
            }
        result['effects'].append({'value':final_dmg,'target':target.position,\
                                  'type':'dmg','is_miss':is_miss,'is_crit':is_crit,\
                                  'tar_max_hp':target.max_hp,'tar_hp':target.card.hp})
        self.dun.result.append(result)
        
    def __get_final_dmg(self,attr,target,dmg,dmg_type='phys'):    
        """伤害计算
        """
        is_miss = 0 #miss
        is_crit = 0 #暴击
        final_dmg = 0 #最终的伤害
        final_miss = target.evasion_rate - attr.invasion_rate
        if final_miss > 0 and utils.is_happen(abs(final_miss)*0.01):
            is_miss = 1
            return final_dmg,is_miss,is_crit
        
        final_crit = attr.critical_rate - target.durability_rate
        if final_crit > 0 and utils.is_happen(abs(final_crit)*0.01):
            is_crit = 1
            
        #获取防御吸收之后的伤害 
        lv_diff = (attr.card.lv - target.card.lv) * 0.01 #等级差修正=（攻击方等级-防御方等级）    
        if lv_diff > 0.2:
            lv_diff = 0.2
        elif lv_diff < -0.2:
            lv_diff = -0.2 
        defense = target.physDef
        if dmg_type == 'phys':
            defense = target.physDef if target.physDef < 0.75 else 0.75#防御能力（物抗或魔抗/（0.5+人物等级*1.5））%
        else:    
            defense = target.magDef if target.magDef < 0.75 else 0.75 #防御能力（物抗或魔抗/（0.5+人物等级*1.5））%
        dmg_cut_rate = defense - (1* lv_diff)#伤害吸收率=防御方防御能力-(1*等级差修正)
        final_dmg = dmg * (1 - dmg_cut_rate) #攻击伤害*（1-伤害吸收率）
    
        #增加伤害buff
        if '5' in attr.buff_list:
            final_dmg += final_dmg * attr.buff_list['5']['value']
            
        #附加魔法伤害buff     
        if '6' in attr.buff_list:
            defense = target.magDef if target.magDef < 0.75 else 0.75 
            dmg_cut_rate = defense - (1* lv_diff)
            final_dmg = dmg * (1 - dmg_cut_rate)
            final_dmg += final_dmg * attr.buff_list['6']['value']
            
        #减少受到的伤害buff  
        if '7' in target.buff_list:
            final_dmg -= final_dmg * target.buff_list['7']['value']
            
        #减少伤害buff    
        if '8' in attr.buff_list:
            final_dmg -= final_dmg * attr.buff_list['8']['value']
            
        #检查是否有冰甲
        if '13' in target.buff_list:
            target.buff_list['13']
            effect_rate = target.buff_list['13']["effect_rate"]
            effect_rate_turns = target.buff_list['13']["effect_rate_turns"] 
            if utils.is_happen(effect_rate):
                attr.buff_list["11"] = {"turns":effect_rate_turns}
        
        if is_crit == 1:
            final_dmg += (final_dmg * 0.8)
            
        return int(final_dmg),is_miss,is_crit