#-*- coding: utf-8 -*-
import copy
import random
from apps.common import utils
from apps.models.user_teams import UserTeams
from apps.config import game_config

def teams_info(oc_user,params):
    """佣兵信息
    """
    data = {}
    user_team_obj = UserTeams.get_instance(oc_user.uid)        
    data['teams_info'] = user_team_obj.teams_info
    data['develop_info'] = user_team_obj.develop_info
    data['team'] = user_team_obj.team
    return 0,data

def develop_start(oc_user,params):
    """计算培养的结果,
        参数 dtype：培养类型，mid：培养目标
        返回值{'vitality':-1,'strength':1,'stealth':2,'intelligence':3}
    """
    dtype = int(params.get('type',1))
    tid = params['tid']
    team_develop_config = game_config.team_config["team_develop_config"][str(dtype)]
    cost_type = team_develop_config['cost_type']
    cost = int(team_develop_config['cost'])
    #扣金钱
    if cost > oc_user.property_info.property_info[cost_type]:
        return 1,{'msg':u'金币不够！'}  

    vip_config = game_config.vip_config[oc_user.property_info.vip_lv]
    team_develop = int(vip_config["team_develop"])
    if team_develop < dtype:
        return 2,{"msg":"您不能选择此类培养"}
    
    oc_user.property_info.property_info[cost_type] -= cost
    oc_user.property_info.put()   
    #培养
    add_rate = team_develop_config['add_rate']
    addrate_minus = team_develop_config['addrate_minus']
    deduction = team_develop_config['deduction']
    addition = team_develop_config['addition']
    add_max_base = team_develop_config['add_max']
    lv = oc_user.property_info.property_info['lv']
    add_max =  int(add_max_base) * int(lv) #当前等级培养的最大值
    user_teams_obj =  UserTeams.get_instance(oc_user.uid)
    develop_current = user_teams_obj.develop_info[tid] #当前已经培养的值
    result = {}
    for attr in ['vitality', 'strength', 'stealth', 'intelligence']:
        minus = float(develop_current[attr])/add_max - addrate_minus
        if minus <= 0:
            develop_rate = add_rate
        else:
            develop_rate = add_rate - minus
            if develop_rate < 0.2:
                develop_rate = 0.2

        if utils.is_happen(develop_rate):
            if minus > 0:
                develop_num = random.randint(addition[0], addition[1]/2)                
            else:
                develop_num = random.randint(addition[0], addition[1])                
        else:
            develop_num = random.randint(-deduction[1], -deduction[0])
        result[attr] = develop_num

    user_teams_obj.develop_last = result
    user_teams_obj.put()
    return 0,{'result':result}
    
def develop_end(oc_user,params):
    """保存培养的结果
        参数 dtype：培养类型，mid：培养目标
        返回值{ 'vitality':-1,'strength':1,'stealth':2,'intelligence':3}
    """
    tid = params['tid']
    #写入培养信息
    user_teams_obj = UserTeams.get_instance(oc_user.uid)
    develop_last = user_teams_obj.develop_last
    if not develop_last:
        return 1,{'msg':u'培养无效'}
    
    for i in ['vitality','strength','stealth','intelligence']:
        user_teams_obj.develop_info[tid][i] += develop_last[i] 
    user_teams_obj.develop_last = {}
    user_teams_obj.put()
    return 0,{}

def team_dungeon(oc_user,params):
    """让当前的佣兵出站
    """
    tid = params.get('tid',1)
    user_teams_obj = UserTeams.get_instance(oc_user.uid)
    if tid == 0:
        user_teams_obj.team = []
    else:
        user_teams_obj.team = [tid]
    user_teams_obj.put()
    return 0,{}

def refresh_skill(oc_user,params):
    """刷新当前技能
    """
    tid = params.get('tid',1)
    lock = params.get('lock')
    user_teams_obj = UserTeams.get_instance(oc_user.uid)
    teams_info = user_teams_obj.teams_info[tid]
    skill_list = teams_info["skill_list"]
    refresh_num = teams_info["refresh_num"]
    
    #判断前端发来的技能技能个数是不个数
    skillSlot_unlock = game_config.card_level_config["skillSlot_unlock"]
    lv = oc_user.property_info.lv
    lock = lock.split(',')
    if (lv < 25) or (skillSlot_unlock[str(len(lock))] > lv):
        return 1,{"msg":u"您的等级还没达到"}
        
    #先判断消耗
    if refresh_num >=3:
        team_skill_refresh_config = game_config.team_config["team_skill_refresh_config"]
        if (str(refresh_num + 1)) not in team_skill_refresh_config:
            max_cost_id = max([int(obj) for obj in team_skill_refresh_config.keys()])
            cost = team_skill_refresh_config[str(max_cost_id)]
        else:
            cost = team_skill_refresh_config[str(refresh_num + 1)]            
        #判断不行
        if not oc_user.property_info.minus_diamond(cost):
            return 2,{"msg":u"您的钻石不够"} 
    
    lock_info = {}
    lock_skill_list = []
    for index,obj in enumerate(lock):
        lock_info[str(index+1)] = obj
        if obj == '1':
            lock_skill_list.append(skill_list[str(index+1)]["skill"])
            
    skill_config = copy.deepcopy(game_config.card_config['ca_'+str(int(tid)+3)]["skill"])                        
    skill_config = [obj for obj in skill_config if obj not in lock_skill_list]
    for k,v in lock_info.items():
        if v == '1':
            skill_list[k]["is_lock"]= 1
        else:
            skid = utils.random_choice(skill_config, 1)[0]
            if k not in skill_list:
                skill_list[k] = {}
            skill_list[k]["skill"] = skid
            skill_list[k]['is_lock'] = 0
            skill_config.remove(skid)
             
    user_teams_obj.teams_info[tid]["refresh_num"] += 1
    user_teams_obj.put()
    return 0,{"result":skill_list}