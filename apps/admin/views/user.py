#-*- coding:utf-8 -*-
#import copy

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from apps.admin.decorators import require_permission
from apps.common.utils import timestamp_toString
from apps.config import game_config

from apps.models.account_mapping import AccountMapping
from apps.models.user_base import UserBase
from apps.models.user_property import UserProperty
from apps.models.user_cards import UserCards
#from apps.models.virtual.card import Card
from apps.models.user_dungeon import UserDungeon
from apps.models.user_login import UserLogin
from apps.models.config import Config
from apps.models.user_equipments import UserEquipments
from apps.models.user_material import UserMaterial
from apps.models.user_teams import UserTeams
from apps.models.compete_rank import get_compete_rank
from apps.models.user_compete import UserCompete

def index(request):
    """用户管理导航页
    """
    status = request.GET.get("status")
    user_type = request.GET.get("user_type",'')
    subareas_conf = eval(Config.get('subareas_conf').data)
    subareas_conf = sorted(subareas_conf.items(),key=lambda x:x[0],reverse=True)    
    return render_to_response('user/index.html',\
                              {"status":status,"user_type":user_type,'subareas_conf':subareas_conf},\
                              RequestContext(request))

@require_permission
def edit_user(request):
    """编辑用户页
    """
    uid = request.GET.get('uid','').strip()
    if not uid:
        pid = request.GET.get('pid','').strip()
        subarea = request.GET.get('subarea','1')
        if pid and subarea:
            account = AccountMapping.get(pid)
            if not account:
                return HttpResponseRedirect('/admin/user/?status=1')
            
            uid = account.get_subarea_uid(subarea)
            if not uid:
                return HttpResponseRedirect('/admin/user/?status=1')
        else:
            return HttpResponseRedirect('/admin/user/?status=1')
            
    user = UserBase.get(uid)
    if not user:
        return HttpResponseRedirect('/admin/user/?status=1')

    user_property_obj = UserProperty.get(uid)
    user_card_obj = UserCards.get(user.uid)
    user_login_obj = UserLogin.get_instance(user.uid)
    user_equipments_obj = UserEquipments.get_instance(user.uid)
    user_material_obj = UserMaterial.get_instance(user.uid)
    user_dungeon_obj = UserDungeon.get_instance(user.uid)
    user_teams_obj = UserTeams.get_instance(user.uid)
    compete_rank_obj = get_compete_rank(user.subarea)
    user_compete_obj = UserCompete.get_instance(user.uid)
    #提交状态
    if request.method == "POST":            
        state = int(request.POST.get("state","0"))
        state = bool(state)
        #冻结
        if state != user.in_frozen:
            if state:
                user.froze()
            #解冻
            else:
                user.unfroze()
                
        #删除账号        
        if request.POST.get("delete_user",''):
            account = AccountMapping.get(user.pid)
            account.subarea_uids.pop(user.subarea)
            account.put()
            
        #加钻石           
        if request.POST.get('add_diamond',''):
            add_diamond = int(request.POST.get('add_diamond'))
            if add_diamond > 0:
                user.property_info.add_diamond(add_diamond,where='qa_add')
            else:
                user.property_info.minus_diamond(add_diamond)                
        #增加铜钱
        if request.POST.get('add_coin',''):
            add_coin = int(request.POST.get('add_coin'))
            if add_coin > 0:
                user.property_info.add_coin(add_coin,where='qa_add')
            else:
                user.property_info.minus_coin(add_coin)
 
        #增加经验
        if request.POST.get('add_exp',''):
            add_exp = int(request.POST.get('add_exp'))
            user.property_info.add_exp(add_exp,where='qa_add')

        #增加荣誉
        if request.POST.get('add_cp',''):
            add_cp = int(request.POST.get('add_cp'))
            user.property_info.add_cp(add_cp,where='qa_add')

        #增加熔炼值
        if request.POST.get('add_smelting',''):
            add_smelting = int(request.POST.get('add_smelting'))
            user.property_info.add_smelting(add_smelting,where='qa_add')

        #增加声望
        if request.POST.get('add_popularity',''):
            add_popularity = int(request.POST.get('add_popularity'))
            user.property_info.add_popularity(add_popularity,where='qa_add')
                                         
        #增加装备
        if request.POST.get('add_equip',''):            
            add_equip = request.POST.get('add_equip')
            add_equip = add_equip.split(':')
            eid = add_equip[0]
            #lv = int(add_equip[2])
            quality = int(add_equip[1])
            user_equipments_obj.add_equipment(eid,quality, add_type="qa")   

        #增加道具
        if request.POST.get('add_material',''):            
            add_material = request.POST.get('add_material')
            add_material = add_material.split(':')
            mid = add_material[0]
            num = int(add_material[1])
            user_material_obj.add_material(mid,num) 
        
        #增加道具
        if request.POST.getlist('add_mats'):            
            strItemsInfo = request.POST.getlist("add_mats")
            for mid in strItemsInfo:
                user_material_obj.add_material(mid,1) 
            
        #一键增加道具         
        if request.POST.get('give_all_materials',''):           
            num = request.POST.get('all_materials_num')
            for mid in game_config.material_config:
                user_material_obj.add_material(mid,int(num)) 
                
        #一键删除道具         
        if request.POST.get('del_all_materials',''):
            user_material_obj.materials = {} 
            user_material_obj.put()
            
        #一键删除装备        
        if request.POST.get('del_all_equipments',''):
            puton_equip_list = user_equipments_obj.get_puton_equip()
            for eqdbid in user_equipments_obj.equipments.keys():
                if eqdbid not in puton_equip_list:
                    user_equipments_obj.equipments.pop(eqdbid)
            user_equipments_obj.put()    
           
        #装备到角色
        if request.POST.get('equip_puton',''):            
            eid = request.POST.get('eid')
            epart = request.POST.get('epart')
            user_equipments_obj.put_on(eid, epart, '0')

        #装备删除
        if request.POST.get('equip_delete',''):            
            eid = request.POST.get('eid')
            user_equipments_obj.single_sell(eid)
            
        #开放战场
        if request.POST.get('open_dungeon',''):
            open_dungeon = request.POST.get('open_dungeon')            
            user_dungeon_obj.dungeon_info['max_floor_id'] = open_dungeon
            user_dungeon_obj.put()
            
        #设置竞技排名
        if request.POST.get('set_rank',''):
            rank = int(request.POST.get('set_rank'))
            #自己的排名
            my_rank = user_compete_obj.my_rank   
            #rank的uid
            rank_uid = compete_rank_obj.get_name_by_score(rank,rank)            
            if rank_uid:
                compete_rank_obj.set(rank_uid[0],my_rank)
            compete_rank_obj.set(uid,rank)
            
        #修改vip等级
        if request.POST.get('modify_vip_lv'):
            vip_lv = request.POST.get('modify_vip_lv')
            vip_conf = game_config.vip_config.get(str(vip_lv))
            if vip_conf:
                charge = vip_conf['charge']
                user_property_obj.property_info["charge_sum"] = charge/10
                user_property_obj.put()

    data = {
        'property_info':user_property_obj.property_info,
        'user':user,
        'user_card_obj':user_card_obj,
        'card_obj':user_card_obj.card_obj(),
        'add_time':timestamp_toString(user.add_time),        
        'last_login_time':timestamp_toString(user_login_obj.login_info["login_time"]),
        'user_equipments':user_equipments_obj.equipments,
        'get_puton_equip':user_equipments_obj.get_puton_equip,
        'user_category':game_config.card_config[user_card_obj.cid]["category"],
        'user_materials':sorted(user_material_obj.materials.items(),key=lambda x:x[0]),        
        'all_materials':sorted(game_config.material_config.items(),key=lambda x:x[0]),
        'my_rank':user_compete_obj.my_rank,
        'my_vip':user_property_obj.vip_lv

    }
    #佣兵信息
    if '1' in user_teams_obj.teams_info:
        data['team1_obj'] = user_teams_obj.card_obj('1')
        data['team1_equipments'] = user_teams_obj.teams_info['1']["equipments"]        
    if '2' in user_teams_obj.teams_info:        
        data['team2_obj'] = user_teams_obj.card_obj('2')
        data['team2_equipments'] = user_teams_obj.teams_info['2']["equipments"]
    if '3' in user_teams_obj.teams_info:
        data['team3_obj'] = user_teams_obj.card_obj('3')
        data['team3_equipments'] = user_teams_obj.teams_info['3']["equipments"]
        
    #战场信息      
    data["dungeon_info"] = user_dungeon_obj.dungeon_info    
    data['all_dungeon'] = sorted(game_config.dungeon_config.keys(),key=lambda x:int(x))
    data['max_dungeon'] = False
    if data['all_dungeon'][-1] == data["dungeon_info"]["max_floor_id"]:
        data['max_dungeon'] = True
    #登陆信息
    data['login_record'] = UserLogin.get(user.uid).login_info.get('login_record',[])
    data['status'] = 1    
    return render_to_response('user/edit.html',data,RequestContext(request))

def view_user(request):
    """更新用户信息
    """
    uid = request.GET.get('uid','').strip()
    if not uid:
        pid = request.GET.get('pid','').strip()
        if not pid:
            username = request.GET.get('username','')
            if not username:
                return HttpResponseRedirect('/admin/user/?status=1')
            try:
                uid=ocapp.mongo_store.mongo.db['username'].find({'name':username})[0]['uid']
            except:
                return HttpResponseRedirect('/admin/user/?status=1')
        else:
            account = AccountMapping.get(pid)
            if not account:
                return HttpResponseRedirect('/admin/user/?status=1')
            uid = account.get_subarea_uid('1')
 
    user = UserBase.get(uid)
    if not user :
        return HttpResponseRedirect('/admin/user/?status=1')

    user = UserBase.get(uid)
    if not user:
        return HttpResponseRedirect('/admin/user/?status=1')

    user_property_obj = UserProperty.get(uid)
    user_card_obj = UserCards.get(user.uid)
    user_login_obj = UserLogin.get_instance(user.uid)
    user_equipments_obj  = UserEquipments.get(user.uid)
  
    data = {
        'property_info':user_property_obj.property_info,
        'user':user,
        'user_card_obj':user_card_obj,
        'card_obj':user_card_obj.card_obj(),
        'add_time':timestamp_toString(user.add_time),        
        'last_login_time':timestamp_toString(user_login_obj.login_info["login_time"]),
        'user_equipments':user_equipments_obj.equipments
    }
    #用户当前战场信息
    user_dungeon_obj = UserDungeon.get_instance(user.uid)
    data["dungeon_info"] = user_dungeon_obj.dungeon_info
    #登陆信息
    data['login_record'] = UserLogin.get(user.uid).login_info.get('login_record',[])

    return render_to_response('user/view.html',data,RequestContext(request))
