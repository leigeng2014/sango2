#-*- coding: utf-8 -*-
import datetime
import traceback
from apps.oclib.model import LogModel
from apps.common import utils
from apps.config import game_config

def set_log(class_type,**argw):
    write_tag = game_config.system_config.get('log_control', True)
    if not write_tag:
        return
    bl_obj = __import__('data_log_mod',globals(),locals())
    try:
        bl_class = getattr(bl_obj, class_type)
        bl_class.set_log(**argw)
    except:
        utils.debug_print('---class---%s' % class_type)
        utils.debug_print(traceback.format_exc())
        
class DataLogModel(LogModel):
    pk = 'uid'
    fields = ['uid', 'subarea']

    @classmethod
    def set_log(cls,**argw):
        obj = cls()
        obj.date_time = datetime.datetime.now()
        [setattr(obj, k, argw.get(k)) for k in argw]
        obj.put()
        
        
class CoinProduct(DataLogModel):
    #"""
    #coin 产出
    #"""
    fields = ['uid', 'subarea', 'date_time', 'where', 'user_lv', 'sum', 'before', 'after']


class CoinConsume(DataLogModel):
    #"""
    #coin 消耗,这个是记录元宝的详细信息，
    #"""
    fields = ['uid', 'subarea', 'date_time', 'where', 'user_lv', 'sum', 'before', 'after']
    
class ConsumeRecord(DataLogModel):
    #"""
    #元宝的消耗记录，用于统计类似于复活等消耗的元宝
    #"""
    fields = ['uid', 'subarea', 'lv','num','createtime','consume_type','before_coin','after_coin']

    @classmethod
    def set_consume_record(cls, uid, subarea, lv=1, num=0, consume_type='', before_coin=0, after_coin=0):
        obj = cls()
        obj.uid = uid
        obj.subarea = subarea
        obj.lv = lv
        obj.num = num
        obj.createtime = utils.datetime_toString(datetime.datetime.now())
        obj.consume_type = consume_type
        obj.before_coin = before_coin
        obj.after_coin = after_coin
        obj.put() 

class GoldProduct(DataLogModel):
    #"""
    #金币的产生
    #"""
    pk = 'uid'
    fields = ['uid','date_time','where','user_lv','sum', 'before', 'after', ]
 
class GoldConsume(DataLogModel):
    #"""
    #金币的消耗
    #"""
    fields = ['uid', 'subarea', 'date_time', 'where', 'user_lv', 'sum', 'before', 'after']
    
class CardProduct(DataLogModel):
    #"""
    #武将的产生
    #"""
    fields = ['uid', 'subarea', 'date_time', 'where', 'ucid', 'card_msg']

class CardConsume(DataLogModel):
    #"""
    #武将的消耗
    #"""
    fields = ['uid', 'subarea', 'date_time', 'card_msg', 'ucid', 'where']  

class CardDeck(DataLogModel):
    #"""
    #武将的编队
    #"""
    fields = ['uid', 'subarea', 'date_time','lv']  

class CardUpdate(DataLogModel):
    #"""
    #武将的升级
    #"""
    fields = ['uid', 'subarea', 'date_time', 'card_msg', 'ucid', 'where','old_exp','old_lv']  
       
class CardUpdateSkill(DataLogModel): 
    #"""
    #武将的技能升级
    #"""
    fields = ['uid', 'subarea', 'date_time', 'card_msg', 'ucid', 'where','old_sk_exp','old_sk_lv']  
    
class EvolutionProduct(DataLogModel):
    #"""
    #武将的产生
    #"""
    fields = ['uid', 'subarea', 'date_time', 'where', 'ecid', 'old_num','new_num','add_num']

class EvolutionConsume(DataLogModel):
    #"""
    #武将的消耗
    #"""
    fields = ['uid', 'subarea', 'date_time', 'where', 'ecid','old_num','new_num','consume_num']  
    
class DungeonRecord(DataLogModel):
    #"""
    #战场的产生
    #"""
    fields = ['uid', 'subarea', 'date_time', 'statement', 'dungeon_id', 'dungeon_type', 
              'card_deck', 'lv','lv_up_flag','dungeon_star_result']


class UserLevelHistory(DataLogModel):
    #"""
    #用户等级
    #"""
    fields = ['uid', 'subarea', 'date_time', 'add_exp', 'old_lv', 'new_lv',
             'old_exp','new_exp','where']
    
    
class UserPvpRecord(DataLogModel):
    #"""用户pvp匹配和结算的信息
    #"""
    fields = ['uid','subarea','mate_uid','deck','score','success_time','sum_time','statement','pvp_did']			  

class ChargeRecord(DataLogModel):
    #"""
    #充值记录
    #"""
    pk = 'oid'
    
