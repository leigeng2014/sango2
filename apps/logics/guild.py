#-*- coding: utf-8 -*-
import copy
import time
import datetime

from apps.common import utils
from apps.common import sequence
from apps.config import game_config

from apps.models.cache_tool import CacheTool
from apps.models.guild_base import GuildBase
from apps.models.guild_user import GuildUser
from apps.models.user_cards import UserCards
from apps.models.user_dungeon import UserDungeon
from apps.models.user_material import UserMaterial
from apps.models.guild_dungeon import GuildDungeon
from apps.models.guild_user_dungeon import GuildUserDungeon
from apps.models.user_base import UserBase
from apps.models.rank import Rank
from apps.models.guild_name import GuildName

def get_guild_info(oc_user,params):
    """获取公会信息
    """
    data = {}
    data["guild_base"] = {}
    data["guild_user"] = {}
    data["guild_dungeon"] = {}
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 0,data
       
    #公会的信息
    guild_base_obj = GuildBase.get(guild_user_obj.gid)
    data["guild_base"]["gnotice"] = guild_base_obj.gnotice #宣言
    data["guild_base"]["condition"] = guild_base_obj.condition
    data["guild_base"]["gname"] = guild_base_obj.gname
    data["guild_base"]["total_num"] = guild_base_obj.total_num
    data["guild_base"]["max_num"] = guild_base_obj.max_num
    data["guild_base"]["lv"] = guild_base_obj.lv
    data["guild_base"]["exp"] = guild_base_obj.gexp
    data["guild_base"]["gid"] = guild_base_obj.gid
    data["guild_base"]["condition"] = guild_base_obj.condition
    data["guild_base"]["next_lv_exp"] = guild_base_obj.next_lv_gexp
    data["guild_base"]["sk_lv"] = guild_base_obj.sk_lv
    data["guild_base"]["shop_lv"] = guild_base_obj.shop_lv
    data["guild_base"]["gcoin"] = guild_base_obj.gcoin
    #公会的个人信息
    data["guild_user"]["last_sign_time"] = guild_user_obj.last_sign_time
    data["guild_user"]["last_contribution_time"] = guild_user_obj.last_contribution_time    
    data["guild_user"]["sign_num"] = guild_user_obj.sign_num
    data["guild_user"]["position"] = guild_user_obj.position
    data["guild_user"]["gcontribution"]  = guild_user_obj.gcontribution
    data["guild_user"]["remain_gcontribution"]  = guild_user_obj.remain_gcontribution
    #公会战斗
    guild_dungeon_obj = GuildDungeon.get_instance(guild_user_obj.gid) 
    guild_dungeon_obj.update_dungeon()
    data["guild_dungeon"]["create_time"] = 0
    data["guild_dungeon"]["dungeon_num"] = len(guild_dungeon_obj.dungeon_record)
    data["guild_dungeon"]["is_enter_dungeon"] = 0
    data["guild_dungeon"]["inspire_num"] = 0
    data["guild_dungeon"]["total_hp"] = 0
    data["guild_dungeon"]["hp"] = 0
    if guild_dungeon_obj.hp > 0:
        data["guild_dungeon"]["create_time"] = guild_dungeon_obj.create_time
        guild_user_dungeon_obj = GuildUserDungeon.get_instance(oc_user.uid)
        if guild_user_dungeon_obj.did == guild_dungeon_obj.did:
            data["guild_dungeon"]["is_enter_dungeon"] = 1
            data["guild_dungeon"]["total_hp"] = guild_dungeon_obj.total_hp
            data["guild_dungeon"]["hp"] = guild_dungeon_obj.hp
            data["guild_dungeon"]["inspire_num"] = guild_user_dungeon_obj.inspire_num
    data["guild_dungeon"]["floor_id"] = guild_dungeon_obj.floor_id
    return 0,data 

def get_guild_member(oc_user,params):
    """获得成员信息
    """    
    data = {}
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 0,{}
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid)
    #会长信息
    leader_user_cards_obj = UserCards.get_instance(guild_base_obj.gleader)
    leader_user_dungeon_obj = UserDungeon.get_instance(guild_base_obj.gleader)
    leader_info = [{"uid":guild_base_obj.gleader,"lv":leader_user_cards_obj.user_base.property_info.lv,\
                    "name":leader_user_cards_obj.user_base.username,"position":"leader",\
                    "last_login_time":leader_user_dungeon_obj.dungeon_info["last"]["enter_date"],\
                    "force":leader_user_cards_obj.force,"cid":leader_user_cards_obj.cid,\
                    "gcontribution":guild_user_obj.gcontribution}]
    #副会长信息
    second_leader_info = []
    for uid in guild_base_obj.gsecondleader:
        temp = {}
        user_cards_obj = UserCards.get_instance(uid)
        user_dungeon_obj = UserDungeon.get_instance(uid)
        guild_user_obj = GuildUser.get_instance(uid)
        temp["uid"] = uid
        temp["force"] = user_cards_obj.force
        temp["lv"] = user_cards_obj.user_base.property_info.lv
        temp["name"] = user_cards_obj.user_base.username
        temp["position"] = "secondleader"
        temp["last_login_time"] = user_dungeon_obj.dungeon_info["last"]["enter_date"] 
        temp["cid"] = user_cards_obj.cid
        temp["gcontribution"] = guild_user_obj.gcontribution
        second_leader_info.append(temp)   
        
    second_leader_info = sorted(second_leader_info,key=lambda x:x["force"],reverse = False)
    #成员信息
    common_member_info = []
    for uid in guild_base_obj.gmember:
        temp = {}
        user_cards_obj = UserCards.get_instance(uid)
        user_dungeon_obj = UserDungeon.get_instance(uid)
        guild_user_obj = GuildUser.get_instance(uid)
        temp["uid"] = uid
        temp["force"] = user_cards_obj.force
        temp["lv"] = user_cards_obj.user_base.property_info.lv
        temp["name"] = user_cards_obj.user_base.username
        temp["position"] = "common"
        temp["last_login_time"] = user_dungeon_obj.dungeon_info["last"]["enter_date"] 
        temp["cid"] = user_cards_obj.cid
        temp["gcontribution"] = guild_user_obj.gcontribution
        common_member_info.append(temp)   
    common_member_info = sorted(common_member_info,key=lambda x:x["force"],reverse = False)
        
    data["result"] = leader_info + second_leader_info + common_member_info
    return 0,data 
    
def create_guild(oc_user, params):
    """创建公会
    """
    uid = oc_user.uid 
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is True:
        return 1,{"msg":u"您已经是公会成员"}
    
    if oc_user.property_info.lv < 18:
        return 2,{"msg":u"您还没达到18级"}
    
    name = params["name"]

    #检查屏蔽字
    if utils.is_sense_word(name):
        return 3,{"msg":u"名字还有屏蔽字"}

    if GuildName.get(name):
        return 3,{"msg":u"该公会名字已经存在"}
    
    if not oc_user.property_info.minus_diamond(300):
        return 4,{"msg":u"您的钻石不足"}
      
    #创建公会基础信息
    gid = sequence.generate_gid()
    try:
        GuildName.set_name(gid, name)
    except:
        return 5,{"msg":u"该公会名字已经存在"}
    guild_base_obj = GuildBase.get_instance(gid)
    guild_base_obj.gname = name
    guild_base_obj.guildbase_info["gleader"] = uid
    guild_base_obj.guildbase_info["create_uid"] = uid
    guild_base_obj.guildbase_info["gnotice"] = ''
    guild_base_obj.put()
    #更新自己的公会个人信息
    guild_user_obj.guilduser_info["gid"] = gid
    guild_user_obj.guilduser_info["name"] = oc_user.username
    guild_user_obj.put()  
    #把公会加入排行帮
    rank_obj = Rank(oc_user.subarea,'guild_rank')
    rank_obj.set(gid, 0)   
    #把公会加入缓存
    cache_tool = CacheTool.get_instance("guild_id" + str(oc_user.subarea))
    cache_tool.set_value(gid)
    return 0, {} 

def select_guild(oc_user,params):
    """推荐公会
    """
    data = {}
    num = int(params.get("num",1))
    cache_tool = CacheTool.get_instance("guild_id" + str(oc_user.subarea))
    cache_value = cache_tool.cache_value
    result = []
    #le = len(cache_value)
    user_cards_obj = UserCards.get(oc_user.uid)
    force = user_cards_obj.force
    guild_list = utils.random_choice(cache_value, 7)
    for gid in guild_list:
        guild_base_obj = GuildBase.get_instance(gid)
        #战力没达到公会条件的排除掉
        if force < guild_base_obj.condition:
            continue    
             
        temp = {}
        temp["gid"] = gid
        temp["gname"] = guild_base_obj.gname
        temp["lv"] = guild_base_obj.lv
        temp["exp"] = guild_base_obj.gexp
        temp["total_num"] = guild_base_obj.total_num
        temp["max_num"] = guild_base_obj.max_num
        result.append(temp)
    data["result"] = result
    data["next_num"] = num + 1
    return 0,data

def guild_rank(oc_user,params):
    """公会排行帮
    """
    data = {}
    rank_obj = Rank(oc_user.subarea,'guild_rank')
    ranking_list = rank_obj.get(20,desc=True)
    data["guild_rank"] = []
    for obj in ranking_list:
        temp = {}
        gid = obj[0]
        guild_base = GuildBase.get(gid)
        if guild_base is None:
            continue 
        temp = {} 
        ##########################
        temp["gname"] = guild_base.gname
        temp["gid"] = guild_base.gid
        temp["gnotice"] = guild_base.gnotice
        temp["exp"] = guild_base.gexp
        objGuildUser = GuildUser.get(guild_base.gleader)
        temp["gleader"] = objGuildUser.name
        temp["lv"] = guild_base.lv
        data["guild_rank"].append(temp) 
        ########################## 
    return 0,data

# def guild_rank(oc_user,params):
#     """公会排行帮
#     """
#     cache_tool = CacheTool.get_instance("guild_id"  + str(oc_user.subarea))
#     cache_value = cache_tool.cache_value
#     lstguild_base = []
#     for gid in cache_value:
#         guild_base_obj = GuildBase.get(gid)
#         lstguild_base.append(guild_base_obj)
#         
#     lstsortedguild_base = sorted(lstguild_base, \
#                             key = lambda x:x.gexp, \
#                             reverse = True)
#     
#     lstguild_base_info = []
#     if len(lstsortedguild_base) >= 50:
#         lstsortedguild_base = lstsortedguild_base[:50]
#     for guild_base in lstsortedguild_base:
#         dictguild_base = __getsortguildinfo(guild_base)
#         if dictguild_base !={}:
#             lstguild_base_info.append(dictguild_base)
#     data = {}
#     data["guild_rank"] = lstguild_base_info
#     return 0,data
# 
# def __getsortguildinfo(guild_base):
#     #"""获得排序的国家信息
#     #"""
#     if guild_base is None:
#         return {} 
#     dictguild_base = {}
#     dictguild_base["gname"] = guild_base.gname
#     dictguild_base["gid"] = guild_base.gid
#     dictguild_base["gnotice"] = guild_base.gnotice
#     dictguild_base["exp"] = guild_base.gexp
#     objGuildUser = GuildUser.get(guild_base.gleader)
#     if objGuildUser is None:
#         return {} 
#     dictguild_base["gleader"] = objGuildUser.name
#     dictguild_base["lv"] = guild_base.lv
#     return dictguild_base
        
def search_guild(oc_user,params):
    """搜索公会
    """
    data = {}
    gid = params.get("gid")
    guild_base_obj = GuildBase.get(gid)
    if not guild_base_obj:
        return 1,{"msg":u"该公会不存在"}
        
    data["gname"] = guild_base_obj.gname
    data["lv"] = guild_base_obj.lv
    data["gid"] = gid
    data["total_num"] = guild_base_obj.total_num
    data["max_num"] = guild_base_obj.max_num
    return 0,{"result":data}

def add_guild(oc_user,params):
    """加入公会
    """
    result = {}
    gid = params.get("gid")
    guild_base_obj = GuildBase.get(gid)
    if not guild_base_obj:
        return 1,{"msg":u"该公会不存在"}
    
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is True:
        return 2,{"msg":u"您已经是公会成员"}
    
    quit_guild_time = guild_user_obj.quit_guild_time
    if quit_guild_time != '':
        now = datetime.datetime.now()
        quit_guild_time = utils.timestamp_toDatetime(quit_guild_time)
        if (guild_user_obj.is_self_quit == 1) and (now - quit_guild_time).total_seconds() < 60*60*24 :
            return 3,{"msg":u"您退出公会时间还不到24小时"}
        
        elif (guild_user_obj.is_self_quit == 2) and (now - quit_guild_time).total_seconds() < 60*5:
            return 4,{"msg":u"您退出公会时间还不到5分钟"}        
        
    if guild_base_obj.total_num >= guild_base_obj.max_num:
        return 5,{"msg":u"该公会已经满了"}
    
    user_cards_obj = UserCards.get(oc_user.uid)
    if user_cards_obj.force < guild_base_obj.condition:
        return 6,{"msg":u"你的战力还没有达到"}
    
    guild_base_obj.guildbase_info["gmember"].append(oc_user.uid)   
    guild_base_obj.put() 
    
    guild_user_obj.guilduser_info["gid"] = gid
    guild_user_obj.guilduser_info["name"] = oc_user.username
    guild_user_obj.put()  
    return 0,{"result":result}

def quit_guild(oc_user,params):
    """退出公会
    """  
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":"你还没有加入公会"}    
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    if guild_base_obj.gleader == oc_user.uid:
        temp = []
        members = guild_base_obj.gsecondleader + guild_base_obj.gmember
        if members:
            for uid in members:
                member_user_obj = GuildUser.get_instance(uid)
                temp.append(member_user_obj)
            temp = sorted(temp,key=lambda x:x.gcontribution)
            max_gcontribution_uid = temp[0].uid        
            if max_gcontribution_uid in guild_base_obj.gsecondleader:
                guild_base_obj.guildbase_info["gsecondleader"].remove(max_gcontribution_uid)
            if max_gcontribution_uid in guild_base_obj.gmember:
                guild_base_obj.guildbase_info["gmember"].remove(max_gcontribution_uid)
            guild_base_obj.guildbase_info["gleader"] = max_gcontribution_uid
        else:
            guild_base_obj.guildbase_info["gleader"] = ''
    else:    
        #从公会中清除自己的信息
        if oc_user.uid in guild_base_obj.guildbase_info["gsecondleader"]:        
            guild_base_obj.guildbase_info["gsecondleader"].remove(oc_user.uid)
        else: 
            guild_base_obj.guildbase_info["gmember"].remove(oc_user.uid)
        
    guild_base_obj.put() 
    #清楚自己的公会信息
    guild_user_obj.guilduser_info["gid"] = None
    guild_user_obj.guilduser_info["is_self_quit"] = 1
    guild_user_obj.guilduser_info["quit_guild_time"] = int(time.time())
    guild_user_obj.put()
    return 0,{}

def delete_member(oc_user,params):
    """会长或副会长删除成员
    """
    uid = params["uid"]
    if oc_user.uid == uid:
        return 1,{"msg":u"自己不能踢自己"}
    
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 2,{"msg":u"您还不是公会成员"}
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    
    if (oc_user.uid not in guild_base_obj.gsecondleader) and (oc_user.uid not in [guild_base_obj.gleader]):
        return 3,{"msg":u"会长或副会长才能踢成员!"}
    
    if (oc_user.uid in guild_base_obj.gsecondleader) and (uid in guild_base_obj.gsecondleader):
        return 4,{"msg":u"副会长只能踢普通成员"}
    
    if uid == guild_base_obj.gleader:
        return 5,{"msg":u"会长不能被剔除"}
    
    #从公会中清除该成员的信息
    if uid in guild_base_obj.guildbase_info["gsecondleader"]:        
        guild_base_obj.guildbase_info["gsecondleader"].remove(uid)
    else: 
        guild_base_obj.guildbase_info["gmember"].remove(uid)
    guild_base_obj.put()
    
    #清楚改成员的公会信息
    delete_guild_user_obj = GuildUser.get_instance(uid)
    delete_guild_user_obj.guilduser_info["gid"] = None
    delete_guild_user_obj.guilduser_info["quit_guild_time"] = int(time.time()) 
    delete_guild_user_obj.guilduser_info["is_self_quit"] = 2 
    delete_guild_user_obj.put() 
    return 0,{}
      
def set_second_leader(oc_user, params):
    """任命副会长
    """
    uid = params["uid"]
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if not guild_user_obj.is_guild_member():
        return 1,{"msg":u"您还不是公会成员"}
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    if guild_base_obj.gleader != oc_user.uid:
        return 2,{"msg":u"你不是会长"}
    
    if len(guild_base_obj.guildbase_info["gmember"]) >= guild_base_obj.lv:
        return 3,{"msg":u"副会长名额已满"}
    
    guild_base_obj.guildbase_info["gmember"].remove(uid) 
    guild_base_obj.guildbase_info["gsecondleader"].append(uid)   
    guild_base_obj.put()
    return 0,{}
     
def delete_second_leader(oc_user, params):
    """罢免副会长
    """
    uid = params["uid"]    
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if not guild_user_obj.is_guild_member():
        return 1,{"msg":u"您还不是公会成员"}
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    if guild_base_obj.gleader != oc_user.uid:
        return 2,{"msg":u"你不是会长"}
    
    if uid not in guild_base_obj.guildbase_info["gsecondleader"]:
        return 3,{"msg":u"该成员不是副会长"}
    
    guild_base_obj.guildbase_info["gsecondleader"].remove(uid) 
    guild_base_obj.guildbase_info["gmember"].append(uid)   
    guild_base_obj.put()
    return 0,{}

def giveupleader(oc_user,params):
    """会长让贤
    """
    uid = params["uid"]
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if not guild_user_obj.is_guild_member():
        return 1,{"msg":u"您还不是公会成员"}
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    if guild_base_obj.gleader != oc_user.uid:
        return 2,{"msg":u"你不是会长"}
    
    if uid not in guild_base_obj.guildbase_info["gsecondleader"]:
        return 3,{"msg":u"该成员不是副会长"}
    
    guild_base_obj.guildbase_info["gleader"] = uid              #任命新会长
    guild_base_obj.guildbase_info["gsecondleader"].remove(uid)  #删除老副会长
    guild_base_obj.guildbase_info["gsecondleader"].append(oc_user.uid) #把自己加入副会长  
    guild_base_obj.put()
    return 0,{}  

def set_guild_notice(oc_user,params):
    """修改公会公告
    """
    notice = params.get("notice",'')
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if not guild_user_obj.is_guild_member():
        return 1,{"msg":u"您还没加入公会"}
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    if guild_base_obj.gleader != oc_user.uid:
        return 2,{"msg":u"你不是会长"}
    
    guild_base_obj.guildbase_info["gnotice"] = notice 
    guild_base_obj.put()
    return 0,{}

def set_guild_condition(oc_user,params):
    """修改入会条件
    """
    condition = params.get("condition",0)
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if not guild_user_obj.is_guild_member():
        return 1,{"msg":u"您还没有加入公会"}
    
    gid = guild_user_obj.gid
    guild_base_obj = GuildBase.get_instance(gid)
    if guild_base_obj.gleader != oc_user.uid:
        return 2,{"msg":u"你不是会长"}
    
    guild_base_obj.guildbase_info["condition"] = int(condition) 
    guild_base_obj.put()
    return 0,{} 

def sign(oc_user,params):
    """公会签到
    """
    data = {}
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还没有加入公会"}  
      
    #更新完就信息
    last_sign_time = guild_user_obj.last_sign_time
    if last_sign_time == str(datetime.datetime.now().date()):
        return 2,{"msg":u"你今天已经签到过了！"}
    
    guild_user_obj.guilduser_info["last_sign_time"] = str(datetime.datetime.now().date())
    guild_user_obj.guilduser_info["sign_num"] += 1    
    guild_user_obj.put()
    #发奖励
    sign_award_config = game_config.guild_config["sign_award"]
    gexp = int(sign_award_config["gexp"])
    coin = int(sign_award_config["coin"])
    gcontribution = int(sign_award_config["gcontribution"])
    guild_user_obj.add_gcontribution(gcontribution)
    oc_user.property_info.add_coin(coin)
    guild_base_obj = GuildBase.get_instance(guild_user_obj.gid)
    guild_base_obj.add_gexp(gexp)
    data["result"] = {
                      "exp":0,
                      "gexp":gexp,
                      "coin":coin,
                      "gcontribution":gcontribution,
                      }
    return 0,data  

def guild_shop(oc_user,params):
    """公会商店
    """ 
    data = {}
    data["result"] = {}
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 0,data
    
    guild_user_obj.refresh_buy_record() #刷新商店购买记录
    shop_config = copy.deepcopy(game_config.guild_config["shop"])
    buy_record = guild_user_obj.buy_record
    guild_base_obj = GuildBase.get_instance(oc_user.uid)

    for k,v in shop_config.items():
        v["cost"] = int(500 *(1+ buy_record[k] * 0.05) *(1 - 0.05 * guild_base_obj.shop_lv))
        
    data["result"]["shop"] = shop_config
    data["result"]["gcontribution"]  = guild_user_obj.gcontribution
    data["result"]["remain_gcontribution"]  = guild_user_obj.remain_gcontribution
    return 0,data

def guild_buy(oc_user,params):
    """公会商店购买
    """     
    sid = params["sid"]
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是公会会员"}

    data = {}
    guild_base_obj = GuildBase.get_instance(oc_user.uid)
    cost = int(500 *(1+ (guild_user_obj.guilduser_info["buy_record"][sid] * 0.05)) *\
               (1 - 0.05 * guild_base_obj.shop_lv))

    if guild_user_obj.minus_gcontribution(cost):
        guild_user_obj.guilduser_info["buy_record"][sid] += 1
        guild_user_obj.put()
        shop_config = game_config.guild_config["shop"][sid]        
        user_material_obj = UserMaterial.get_instance(oc_user.uid)
        data["items"] = user_material_obj.add_material(shop_config["id"],shop_config["num"])
        data["cost"] = int(500 *(1+ guild_user_obj.guilduser_info["buy_record"][sid] * 0.05)*(1 - 0.05 * guild_base_obj.shop_lv))
        return 0,data
    return 2,{"msg":u"你的贡献不够"}

def add_sk_lv(oc_user,params):
    """升级技能学院
    """
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是公会会员"}
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid)
    if oc_user.uid not in [guild_base_obj.gleader]:
        return 2,{"msg":u"你还不是会长"}
    
    sk_lv = guild_base_obj.sk_lv
    cost = game_config.guild_config["sk_lv"][str(sk_lv + 1)]["cost"]
    if guild_base_obj.gcoin < cost:
        return 3,{"msg":u"公会资金不够"}
    
    guild_base_obj.guildbase_info["gcoin"] -= cost
    guild_base_obj.guildbase_info["sk_lv"] += 1
    guild_base_obj.put()
    return 0,{}

def add_shop_lv(oc_user,params):
    """升级公会等级
    """
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是公会会员"}
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid)    
    if oc_user.uid not in [guild_base_obj.gleader]:
        return 2,{"msg":u"你还不是会长"}
    
    shop_lv = guild_base_obj.shop_lv
    cost = game_config.guild_config["shop_lv"][str(shop_lv + 1)]["cost"]
    if guild_base_obj.gcoin < cost:
        return 3,{"msg":u"公会资金不够"}
    
    guild_base_obj.guildbase_info["gcoin"] -= cost
    guild_base_obj.guildbase_info["shop_lv"] += 1
    guild_base_obj.put()
    return 0,{}

def guild_contribute(oc_user,params):
    """公会捐献
    """
    data= {}
    ctype = params["type"]
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是公会会员"}
    
    if guild_user_obj.last_contribution_time == str(datetime.datetime.now().date()):
        return 2,{"msg":u"你今天已经签到过了"}

    gcontribution_config = game_config.guild_config["gcontribution_config"][ctype]
    vip_lv = int(gcontribution_config["vip"]["vip_lv"])
    cost = gcontribution_config["cost"]
    award = gcontribution_config["award"]
    
    if oc_user.property_info.vip_lv < vip_lv:
        return 3,{"msg":u"您的vip等级不够"}
   
    #扣金钱或钻石
    if "coin" in cost:
        if not oc_user.property_info.minus_coin(cost["coin"]):
            return 4,{"msg":u"你的金币不够"}
              
        
    if "diamond" in cost:
        if not oc_user.property_info.minus_diamond(cost["diamond"]):
            return 5,{"msg":u"你的钻石不够"}
    
    #给奖励    
    oc_user.property_info.give_award(award)
    guild_user_obj.guilduser_info["last_contribution_time"] = str(datetime.datetime.now().date())
    guild_user_obj.put()  
    #把奖励内容返回给前端
    data["result"] = award
    return 0, data

def guild_contribute_rank(oc_user,params):
    """公会捐献排行
    """
    data = {}
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 0,{}
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid) 
    #成员信息
    member_info = []
    rank = 0
    my_rank = 1
    for uid in guild_base_obj.all_member:
        rank += 1
        temp = {}
        temp["uid"] = uid
        guild_user_obj = GuildUser.get_instance(oc_user.uid)
        temp["contribute_gcoin"] = guild_user_obj.contribute_gcoin
        temp["lv"] = guild_user_obj.user_base.property_info.lv
        temp["name"] = guild_user_obj.user_base.username
        temp["position"] = guild_user_obj.position
        if uid == oc_user.uid:
            my_rank = rank            
        member_info.append(temp) 

    member_info = sorted(member_info,key=lambda x:x["contribute_gcoin"],reverse = False)
    data["result"] = {}
    data["result"]["member_info"] = member_info
    data["result"]["my_rank"] = my_rank
    data["result"]["my_contribute_gcoin"] = guild_user_obj.contribute_gcoin
    return 0, data

def guild_skill_info(oc_user,params):
    """技能学院信息
    """
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    learn_skill_record = guild_user_obj.learn_skill_record
    guild_skill_config = copy.deepcopy(game_config.guild_config["guild_skill_config"])
    data = {}
    data["result"] = {}
    data["result"]["learn_skill_record"] = learn_skill_record 
    data["result"]["guild_skill_config"] = guild_skill_config         
    return 0,data

def learn_skill(oc_user,params):
    """学习公会技能
    """
    sk_id = int(params["sk_id"])
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是会员"}
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid) 
    learn_skill_record = guild_user_obj.learn_skill_record
    guild_skill_config = game_config.guild_config["guild_skill_config"][str(sk_id)]
    cost = guild_skill_config["cost"]
    sk_lv = guild_skill_config["sk_lv"]
    if sk_lv > guild_base_obj.sk_lv:
        return 2,{"msg":u"你的技能等级还没达到"}
    
    if sk_id in learn_skill_record:
        return 3,{"msg":u"该技能已经学过了"}
    
    if "coin" in cost:
        if not oc_user.property_info.minus_coin(cost["coin"]):
            return 4,{"msg":u"你的金币不够"}
        
    if "gcontribution" in cost:
        if not guild_user_obj.minus_gcontribution(cost["gcontribution"]):
            return 5,{"msg":u"你的贡献不够"}
    
    if  9 <= sk_id:
        if ((sk_id/8 - 1)*8 + sk_id%8)not in learn_skill_record:
            return 6,{"msg":u"您的初级技能还没有学习"}
        
    guild_user_obj.guilduser_info["learn_skill_record"].append(int(sk_id))
    return 0,{}

def open_dungeon(oc_user,params):
    """开启公会boss战
    """
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是会员"}
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid)    
    if (oc_user.uid not in [guild_base_obj.gleader]) and (oc_user.uid not in guild_base_obj.gsecondleader):
        return 2,{"msg":u"只有会长和副会长才能开"} 
       
    guild_dungeon_obj = GuildDungeon.get_instance(guild_user_obj.gid) 
    if not guild_dungeon_obj.is_boss_dead():
        return 3,{"msg":u"战斗还没有结束"} 
        
    if len(guild_dungeon_obj.dungeon_record) >= 2:   
        if not oc_user.property_info.minus_diamond(300):   
            return 4,{"msg":u"你的钻石不够"}
        
    guild_dungeon_obj.opendungeon()   #开启战斗
    #enter_dungeon(oc_user,params)     #进入战斗
    return 0,{}

def enter_dungeon(oc_user,params):
    """加入boss战
    """
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是会员"}  
     
    guild_dungeon_obj = GuildDungeon.get_instance(guild_user_obj.gid)
    if guild_dungeon_obj.is_boss_dead():
        return 2,{"msg":u"战斗已经结束了"}
    
    guild_user_dungeon_obj = GuildUserDungeon.get_instance(oc_user.uid)
    print guild_user_dungeon_obj.did,guild_dungeon_obj.did
    if guild_user_dungeon_obj.did == guild_dungeon_obj.did:
        return 3,{"msg":u"您已经加入boss战了"}
    
    #判断是不是当前的战场，如果不是，则重置自己的信息
    if guild_user_dungeon_obj.did and guild_user_dungeon_obj.did != guild_dungeon_obj.did:
        guild_user_dungeon_obj.refresh_dungeon_info()
        
    #对boss造成伤害
    guild_user_dungeon_obj.did = guild_dungeon_obj.did
    guild_user_dungeon_obj.damage = int(100 +(guild_user_dungeon_obj.inspire_num * 0.1) * 1000)
    guild_dungeon_obj.hp -= guild_user_dungeon_obj.damage
    guild_user_dungeon_obj.put()
    guild_dungeon_obj.put()
    if guild_dungeon_obj.is_boss_dead():
        guild_dungeon_obj.give_award(True,oc_user.uid) 
    return 0,{}
 
def inspire_dungeon(oc_user,params):
    """鼓舞战斗
    """
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是会员"}
  
    guild_user_dungeon_obj = GuildUserDungeon.get(oc_user.uid)
    inspire_max_num = game_config.guild_config.get("inspire_max_num",10)
    if guild_user_dungeon_obj.inspire_num >= inspire_max_num:
        return 2,{"msg":u"鼓舞次数已达到最高"}
        
    if not oc_user.property_info.minus_diamond(20):
        return 3,{"msg":u"你的钻石不够"} 
    
    guild_user_dungeon_obj.inspire_num += 1  
    guild_user_dungeon_obj.put()
    return 0,{}  

def dungeon_rank(oc_user,params):
    """战斗排行
    """
    data = {}
    guild_user_obj = GuildUser.get_instance(oc_user.uid)
    if guild_user_obj.is_guild_member() is False:
        return 1,{"msg":u"你还不是会员"}  
    
    guild_base_obj = GuildBase.get(guild_user_obj.gid)
    guild_dungeon_obj =GuildDungeon.get(guild_user_obj.gid)
    member = []
    for uid in guild_base_obj.all_member:
        guild_user_dungeon_obj = GuildUserDungeon.get_instance(uid)
        damage = 0
        if guild_user_dungeon_obj.did == guild_dungeon_obj.did:
            damage = guild_user_dungeon_obj.damage
        member.append((uid,damage))        
    member = sorted(member,key=lambda x:x[1])
    
    rank = 0
    my_rank = 0
    my_damage = 0
    ranking_list = []
    for uid,damage in member:
        rank += 1
        if uid == oc_user.uid:
            my_rank = rank
            my_damage = damage
        temp = {}
        user_base_obj = UserBase.get(uid)        
        temp["uid"] = uid
        temp["lv"] = user_base_obj.property_info.lv
        temp["name"] = user_base_obj.username
        temp["damage"] = damage        
        ranking_list.append(temp)  
    data["ranking_list"] = ranking_list
    data["my_rank"] = my_rank
    data["my_damage"] = my_damage    
    return 0,{"result":data}
