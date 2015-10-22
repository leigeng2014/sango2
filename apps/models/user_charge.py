#-*- coding: utf-8 -*-
import time

from apps.oclib.model import UserModel

class UserCharge(UserModel):
    #"""用户充值信息
    #"""
    pk = 'uid'
    fields = ['uid','charge_info']
    def __init__(self,uid = None):
        self.uid = uid
        self.charge_info = {
                            'special_first_charge':True,     #是否第一次购买特殊元宝礼包标识(6元30礼包)
                            'first_charge_date':None,        #第一次充值时间
                            'charged_fg':False,              #是否充值的标识（不包含6元30礼包）
                            'double_charge_date':[],         #双倍充值的时间列表
                            'first_charge':True,             #要开双倍的标识
                            'charge_sum_diamond':0,              #充值的总元宝数
                            'charge_sum_money':0,            #充值的总money
                            'charge_record': {},              #充值记录
                            'first_charge_items': [],       # 记录已首充过的item_id
                            }
 
        
    @classmethod
    def get_instance(cls,uid):
        obj = super(UserCharge,cls).get(uid)
        if obj is None:
            obj = cls._install(uid)
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
    def special_first_charge(self):
        return self.charge_info.get('special_first_charge',True) 
       
    @property
    def first_charge_date(self):
        #"""第一次充值的时间
        #"""
        return self.charge_info.get("first_charge_date",None)
    
    @property
    def first_charge(self):
        #"""开双倍的标识
        #"""
        return self.charge_info.get("first_charge",True)
    
    @property
    def charged_fg(self):
        #"""用户充值过与否的标识，不包括6元大礼包
        #"""
        return self.charge_info.get('charged_fg',False)
    
    @property
    def double_charge_date(self):
        #"""记录双倍充值的记录
        #"""
        if len(self.charge_info["double_charge_date"]) > 5:
            self.charge_info["double_charge_date"].pop(0)
            
        return self.charge_info["double_charge_date"] 
    
    @property
    def charge_sum_diamond(self):
        #"""得到该玩家累计的充值元宝个数
        #"""
        return self.charge_info.get("charge_sum_diamond",0)
    
    @property
    def charge_sum_money(self):
        #"""得到该玩家累计的充值的money
        #"""
        return self.charge_info.get("charge_sum_money",0)
    
    def add_charge_sum_diamond(self, diamond_num):
        #"""增加累计的充元宝记录
        #"""
        self.charge_info["charge_sum_diamond"] += diamond_num
        self.put()

    def add_charge_sum_money(self, price):
        #"""增加累计充值的money
        #"""
        self.charge_info["charge_sum_money"] += price
        self.put()
        
    def add_charge_record(self,coin):
        #"""记录在玩家充值情况 
        #"""
        now_time = int(time.time()) 
        self.charge_info['charge_record'][str(now_time)] = coin
        self.put()  
        