#-*- coding: utf-8 -*-
import datetime
from apps.oclib.model import UserModel
from apps.config import game_config

class UserAward(UserModel):
    """用户奖励
    """
    pk = 'uid'
    fields = ['uid','login_award','charge_award','continuous_login_award',\
              'dungeon_award','user_lv_award','sign_record']
    def __init__(self,uid = None):
        self.uid = uid
        self.login_award = []             #开服奖励领取记录
        self.charge_award = []            #充值奖励领取记录
        self.continuous_login_award = {}  #连续登陆未领取奖励记录
        self.sign_award = []              #签到奖励记录
        self.dungeon_award = []           #战场通关奖励记录
        self.user_lv_award = []           #玩家等级奖励记录
        self.sign_record = {'1':[]}       #记录月签到奖励的信息
        
    @classmethod
    def get_instance(cls,uid):
        obj = super(UserAward,cls).get(uid)
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
             
    def get_next_award(self,atype):
        """获取下一个礼包
        """
        result = {"type":atype,"id":''}
        award_config = game_config.award_config
        #开服奖励
        from apps.models.user_login import UserLogin
        user_login_obj = UserLogin.get_instance(self.uid)  
        if atype == "login":                
            last_aid = max([int(i) for i in self.login_award]) if self.login_award else 0
            login_award_list = sorted(award_config["login"].items(),key=lambda x:int(x[0]))
            total_login_num = user_login_obj.login_info["total_login_num"]
            award_list = [] 
            for i in login_award_list:
                if (int(i[0]) > last_aid) and (int(i[0]) <= total_login_num):                
                    award_list.append(i[0])      
            if len(award_list) > 3:
                next_login_aid = award_list[-3]
            elif len(award_list) == 0:
                next_login_aid = total_login_num + 1
            else:
                next_login_aid = award_list[0]

            if str(next_login_aid) not in award_config["login"]:
                next_login_aid = ''
            result = {"type":"login","id":next_login_aid}
        
        elif atype == "sign":                
            last_sign_aid = max([int(i) for i in self.sign_award]) if self.sign_award else 0
            login_award_list = sorted(award_config["sign"].items(),key=lambda x:int(x[0]))
            total_login_num = user_login_obj.login_info["total_login_num"]
            award_list = [] 
            for i in login_award_list:
                if (int(i[0]) > last_sign_aid) and (int(i[0]) <= total_login_num):                
                    award_list.append(i[0])      
            if len(award_list) > 3:
                next_login_aid = award_list[-3]
            elif len(award_list) == 0:
                next_login_aid = total_login_num + 1
            else:
                next_login_aid = award_list[0]

            if str(next_login_aid) not in award_config["login"]:
                next_login_aid = ''
            result = {"type":"sign","id":next_login_aid}
                    
        elif atype == "continuous_login":
            #连续登陆奖励
            if not self.continuous_login_award:
                now = datetime.datetime.now() + datetime.timedelta(days=1) 
                continuous_login_num = user_login_obj.login_info["continuous_login_num"]
                result = {"type":"continuous_login","id":{str(now.date()):continuous_login_num + 1}}
            else: 
                continuous_award_list = sorted(self.continuous_login_award.items(),key=lambda x:x[0])
                result = {"type":"continuous_login","id":dict([continuous_award_list[0]])}
        #充值奖励        
        elif atype == "charge": 
            last_charge_aid = max([int(i) for i in self.charge_award]) if self.charge_award else 0
            charge_award_list = sorted(award_config["charge"].items(),key=lambda x:int(x[0]))
            next_charge_aid = ''
            for i in charge_award_list:
                if int(i[0]) > last_charge_aid:
                    next_charge_aid = i[0]
                    break
            result = {"type":"charge","id":next_charge_aid}
        
        #战场奖励
        elif atype == "dungeon":
            last_dungeon_aid =  max([int(i) for i in self.dungeon_award]) if self.dungeon_award else 0
            dungeon_award_list = sorted(award_config["dungeon"].items(),key=lambda x:int(x[0]))
            next_dungeon_aid = ''
            for i in dungeon_award_list:
                if int(i[0]) > last_dungeon_aid:
                    next_dungeon_aid = i[0]
                    break
            result = {"type":"dungeon","id":next_dungeon_aid}
        
        #等级奖励
        elif atype == "user_lv":
            last_lv_aid = max([int(i) for i in self.user_lv_award]) if self.user_lv_award else 0
            lv_award_list = sorted(award_config["user_lv"].items(),key=lambda x:int(x[0]))
            next_lv_aid = ''
            for i in lv_award_list:
                if int(i[0]) > last_lv_aid:
                    next_lv_aid = i[0]
                    break
            result = {"type":"user_lv","id":next_lv_aid} 
        return result