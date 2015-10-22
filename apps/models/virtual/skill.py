#-*- coding: utf-8 -*-  
import random    
from apps.common import utils      
from apps.config import game_config
class Skill(object):
    '''英雄的技能'''
    #1,造成s%的物理伤害
    #2，造成s%的魔法伤害
    #3，增加s%的最大生命值
    #4，增加s%的最大魔法值
    #5，x回合增加s%的攻击
    #6，x回合增加s%的魔法攻击
    #7，x回合减少%s受到的伤害
    #8, x回合减少%s的伤害
    #9，x回合增加%s的攻击
    #10,x回合眩晕
    #11，x回合冰冻
    #12，x回合中毒，每回合减少%s点hp
    #13，x回合穿上冰甲，冰甲有%s的几率使攻击者冰冻2回合。
    def __init__(self, soilder, skid):
        self.soilder = soilder
        self.conf = game_config.skill_config[skid]  #从config中取数据
        self.skid = skid#技能ID
        self.name = self.conf.get('name','')
        self.mp = self.conf.get('mp',0)
        self.target_list_record = []        #技能每回合的目标记录
        self.first_skill_attr = 0           #技能1中的伤害值（用于吸血）
        self.skill_len = len(self.conf)     #技能长度
        
    def get_target_list(self,target_type,target_num,target_term):
        target_list = []    
        #敌人
        if target_type == 'enemy':
            target_list = self.soilder.enemy_army
        #我军        
        elif target_type == 'mate':
            target_list = self.soilder.our_army
                
        return target_list

    def start(self):
        """释放技能"""
        #发动技能（减少mp，和改变技能释放回合数）
        self.soilder.card.mp -= self.mp  
        #循环技能中的每一个触发条件（多个技能组合）
        result = {'unit':self.soilder.position,'type':self.skid,'effects':[]}
        for i in range(skill_len):
            i = str(i+1)
            if i in self.conf: 
                category = self.conf[i]['category']
                #如果发动技能就触发效果,配置空{}  
                rate = self.conf[i].get('rate',1.0)
                #触发的概率 
                if not utils.is_happen(rate):
                    continue 
                               
                #目标  
                target_list = self.get_target_list(target_type,target_num,target_term)
                if i == '1':
                    self.target_list_record = target_list 
                else:
                    self.target_list_record = []
                ###################################
                dmg = random.randint(int(self.soilder.card.minDamage),int(self.soilder.card.maxDamage))
                for tar in target_list:  
                    if category == '1':
                        #造成物理伤害
                        final_dmg,is_miss,is_crit = get_final_dmg(self.soilder,tar,dmg,dmg_type='phys')                        
                        final_dmg = int(final_dmg * effect_value)
                        tar.card.hp  -= final_dmg
                        first_skill_attr = final_dmg
                        result['effects'].append({'category':category,'value':final_dmg,\
                                                  'target':tar.position,'is_miss':is_miss,\
                                                  'is_crit':is_crit,'category':category})
                    
                    elif category == '2':
                        #造成魔法伤害                        
                        final_dmg,is_miss,is_crit = get_final_dmg(self.soilder,tar,dmg,dmg_type='mag')
                        final_dmg = int(final_dmg * effect_value)
                        tar.card.hp  -= final_dmg
                        first_skill_attr = final_dmg
                        result['effects'].append({'category':category,'value':final_dmg,\
                                                  'target' : tar.position,'is_miss':is_miss,'is_crit':is_crit})
                    
                    elif category == '3':
                        #增加最大生命的%xx
                        if effect_value == 'sTarget':#吸血
                            hp = first_skill_attr
                        else:                        #加hp
                            hp = int(tar.max_hp * effect_value)
                        tar.card.hp  += hp
                        if tar.card.hp > tar.max_hp:
                            tar.card.hp = tar.max_hp
                        result['effects'].append({'target':tar.position,'value':hp,'category':category})
                            
                    elif category == '4':
                        #增加最大魔法值的%xx
                        mp = int(tar.max_mp * effect_value)
                        tar.card.mp  += mp
                        result['effects'].append({'target':tar.position,'value':mp,'category':category})
                        
                    #以下buff，要带到soilder身上的  
                    elif category == '5':
                        #增加%s攻击
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                                 'value':effect_value,
                        }     
                        result['effects'].append({'target':tar.position,'value':int(effect_value*100),'category':category,'turns':effect_turns})                   
                        
                    elif category == '6':
                        #附加%s魔法攻击
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                                 'value':effect_value
                        }
                        result['effects'].append({'target':tar.position,'value':int(effect_value*100),'category':category,'turns':effect_turns})
                        
                    elif category == '7':
                        #减少受到的伤害
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                                 'value':effect_value,
                        }   
                        result['effects'].append({'target':tar.position,'value':int(effect_value*100),'category':category,'turns':effect_turns}) 
                    
                    elif category == '8':
                        #减少%s伤害
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                                 'value':effect_value,
                        }      
                        result['effects'].append({'target':tar.position,'value':int(effect_value*100),'category':category,'turns':effect_turns})
                    
                    elif category == '9':
                        #增加%s防御
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                                 'value':effect_value,
                        } 
                        result['effects'].append({'target':tar.position,'value':int(effect_value*100),'category':category,'turns':effect_turns})                   
                        
                    elif category  == '10':
                        #眩晕
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                        }
                        result['effects'].append({'target':tar.position,'turns':effect_turns,'value':0,'category':category})
                    
                    elif category  == '11':
                        #冰冻
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                        }
                        result['effects'].append({'target':tar.position,'turns':effect_turns,'value':0,'category':category})
                    
                    elif category  == '12':
                        #中毒
                        tar.buff_list[category] = {
                                 'turns':effect_turns,
                                 'value':effect_value
                        }
                        result['effects'].append({'target':tar.position,'turns':effect_turns,'value':int(effect_value*100),'category':category})
                        
                    elif category == '13':
                        #给自己一个冰甲，turns
                        effect_rate = effect.get('effect_rate','')
                        effect_rate_turns = effect.get('effect_rate_turns','')
                        effect_turns = effect.get('effect_turns','')
                        tar.buff_list['13'] = {
                            'effect_rate':effect_rate,    #50%的概率 
                            'effect_rate_turns':effect_rate_turns,     #3个回合内   
                            'turns':effect_turns         
                        }
                        result['effects'].append({'target' : tar.position,'turns':effect_turns,'value':0,'category':category})

        #把信息加入result
        self.soilder.dun.result.append(result)

def get_final_dmg(attr,target,dmg,dmg_type='phys'):    
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

class Buff(object):
    """技能的效果"""
    def __init__(self, **kwargs):
        self.sk = kwargs['sk']
        self.own = self.sk.own
        self.name = ''
        self.bid = kwargs.get('bid', '')
        self.time = kwargs.get('time', 0)
        self.value = kwargs.get('value', 0)
        self.is_dot = False
        self.state = 0
        if self.bid in ['b07', 'd03', 'd04']:
            self.target = self.own
        else:
            self.target = kwargs['target']
        self.target.add_buff(self)

    def update(self):
        if self.time < 0:
            self.end()
            return
        if self.delay > 0:
            self.delay -= 1
            return
        self.action()
        self.time -= 1

    def action(self):
        pass

    def end(self):
        pass

    def add_log(self, **kwargs):
        kw = {
            'unit': self.own.tag,
            'target': self.target.tag,
        }
        kwargs.update(kw)
        self.own.dun.set_result(**kwargs)


class AttackDamageBuff(Buff):
    """物理伤害"""
    def __init__(self, **kwargs):
        super(AttackDamageBuff, self).__init__(**kwargs)

    def action(self):
        #是否命中
        if not self.own.is_hit(self.target):
            return
        #计算攻击力
        atk = self.own.attack * self.coefficient + self.value
        #计算伤害值
        dmg = atk * atk / (8 * (self.target.defence - self.own.impale) + atk)
        #对方是否闪避了
        if self.target.is_dodge():
            return
        #吸取生命
        if self.sk.hp_absorption is not None:
            self.own.add_hp(-(dmg * self.sk.hp_absorption['value']))
        #暴击
        if self.own.is_crit(self.target):
            dmg *= 2
        #斩杀
        if self.sk.beheaded and self.target.hp / self.target.hp_max < 0.3:
            dmg *= 2
            self.add_log(id=10)
        #伤害
        if self.target.damage(dmg, 1, self):   # 对方死了返回True
            self.own.add_energy(300)


class MagicDamageBuff(Buff):
    """魔法伤害"""
    def __init__(self, **kwargs):
        super(MagicDamageBuff, self).__init__(**kwargs)

    def action(self):
        #计算攻击力
        atk = self.own.magic * self.coefficient + self.value
        #计算伤害值
        dmg = atk * atk / (8 * (self.target.magic_defence - self.own.ignore_magic_defence ) + atk)
        #吸取生命
        if self.sk.hp_absorption is not None:
            self.own.add_hp(-(dmg * self.sk.hp_absorption['value']))
        #暴击
        if self.own.is_magic_crit(self.target):
            dmg *= 2
        #斩杀
        if self.sk.beheaded and self.target.hp / self.target.hp_max < 0.3:
            dmg *= 2
            self.add_log(id=10)
        #伤害
        if self.target.damage(dmg, 2, self):  #对方死了返回True
            self.own.add_energy(300)