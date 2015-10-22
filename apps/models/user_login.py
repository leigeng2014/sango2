#-*- coding: utf-8 -*-
import time
import datetime

from apps.common import utils
from apps.oclib.model import UserModel
from apps.config import game_config
from apps.models.user_dungeon import UserDungeon
from apps.models.level_user import LevelUser
from apps.models.user_mail import UserMail
from apps.models.user_property import UserProperty

class UserLogin(UserModel):
    #"""用户Login信息    
    #"""
    pk = 'uid'
    fields = ['uid','login_info']    
    def __init__(self, uid=None):
        self.uid = uid  # 用户uid
        self.login_info = {
                            'continuous_login_num':0,    # 连续Login的天数
                            'total_login_num':0,
                            'login_time':utils.datetime_toTimestamp(\
                                        datetime.datetime.now()-datetime.timedelta(days=1)),   # 最后一次Login的时间
                            'login_record':[],#登录记录
                            'system_mail_record':[]#系统邮件列表
                        }

    @classmethod
    def get_instance(cls, uid):
        obj = super(UserLogin,cls).get(uid)
        if not obj:
            obj = cls(uid)
            obj.put()
        return obj
    
    @classmethod
    def get(cls,uid):
        obj = super(UserLogin,cls).get(uid)
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    @property
    def system_mail_record(self):
        if 'system_mail_record' not in self.login_info:
            self.login_info["system_mail_record"] = []
            self.put()
        return self.login_info["system_mail_record"]
    
    def login(self,params):
        """登录
        """        
        now = datetime.datetime.now()
        LevelUser.get_instance(self.user_base.subarea).add_user(self.uid)
        if now.date() != utils.timestamp_toDatetime(self.login_info['login_time']).date():
            #######
            LevelUser.get_instance(self.user_base.subarea).add_user(self.uid) 
            self.login_info['total_login_num'] += 1
            self.login_info['login_record'].insert(0,str(now.date()))
            if len(self.login_info['login_record']) > game_config.system_config.get('login_record_length',30):
                self.login_info['login_record'].pop()
            #连续登录
            if now.date() == (utils.timestamp_toDatetime(self.login_info['login_time']) + datetime.timedelta(days=1)).date():
                self.login_info['continuous_login_num'] += 1
            #非连续登录
            else:
                self.login_info['continuous_login_num'] = 1
            
            #连续登陆
            from apps.models.user_award import UserAward
            user_award_obj = UserAward.get_instance(self.uid)
            user_award_obj.continuous_login_award[str(now.date())] = self.login_info['continuous_login_num']
            user_award_obj.put()
            
            #竞技发奖励
            from apps.models.user_compete import UserCompete
            user_compete_obj = UserCompete.get_instance(self.uid)
            user_compete_obj.send_rank_reward()
            
            #更新每日信息
            self.update_dungeon()
            self.update_compete()
            self.update_forge()
            self.update_shop()
            self.month_plan()
             
        #系统邮件
        self.get_system_mail()
        #登录时间更新
        self.login_info['login_time'] = int(time.time())
        self.put()
        
    def update_dungeon(self):
        """更新每日战场信息
        """
        user_dungeon_obj = UserDungeon.get_instance(self.uid)
        user_dungeon_obj.dungeon_info["dun_boss_num"] = 3
        user_dungeon_obj.dungeon_info["buy_dun_boss_num"] = 0
        user_dungeon_obj.dungeon_info["buy_fast_dun_num"] = 0
        user_dungeon_obj.dungeon_info["expedition_today_record"] = []        
        user_dungeon_obj.put()
        
    def update_compete(self):
        """更新每日竞技场信息
        """
        from apps.models.user_compete import UserCompete
        user_compete_obj = UserCompete.get_instance(self.uid)
        user_compete_obj.compete_info["compete_num"] = 5
        user_compete_obj.compete_info["buy_num"] = 0
        user_compete_obj.put()
        
    def update_forge(self):
        """更新每日装备打造信息
        """
        from apps.models.user_forge import UserForge
        user_forge_obj = UserForge.get_instance(self.uid)
        user_forge_obj.free_times = 2
        user_forge_obj.forge()
        user_forge_obj.put()
        
    def update_shop(self):
        """更新商店
        """
        from apps.models.user_shop import UserShop
        user_shop_obj = UserShop.get_instance(self.uid)
        user_shop_obj.cp_refresh("common") #刷新荣誉商店
        user_shop_obj.cp_refresh_num = 0
        user_shop_obj.cp_refresh_date = int(time.time())
         
        user_shop_obj.common_refresh()     #刷新商店
        user_shop_obj.common_refresh_num = 0
        user_shop_obj.common_refresh_date = int(time.time())
        
        user_shop_obj.buy_coin_num = 0    #购买金币的次数
        user_shop_obj.coin_refresh_date = int(time.time())
        user_shop_obj.put()
    
    def get_system_mail(self):
        """系统邮件
        """
        now = datetime.datetime.now()
        mail_config = game_config.mail_config
        for k in mail_config: 
            if k not in self.system_mail_record:
                start_time = datetime.datetime.strptime(mail_config[k]["start_time"],'%Y-%m-%d %H:%M:%S')
                end_time = datetime.datetime.strptime(mail_config[k]["end_time"],'%Y-%m-%d %H:%M:%S')
                if (now >= start_time) and (end_time >= now):
                    mid = utils.create_gen_id()
                    user_mail = UserMail.hget(self.uid,mid)
                    mtype = mail_config[k]["type"]
                    content = mail_config[k]["content"]
                    awards = mail_config[k].get("awards",{})
                    user_mail.set_mail(mtype=mtype,content=content,awards=awards)
                    self.login_info["system_mail_record"].append(k)
                    self.put()

    def month_plan(self):
        """更新月卡
        """
        now_day = str(datetime.datetime.now().date())
        user_property_obj = UserProperty.get(self.uid)
        month_plan_end_time = user_property_obj.month_plan_end_time
        if month_plan_end_time == '':
            return ''

        if month_plan_end_time < now_day:
            return ''

        if now_day in user_property_obj.month_plan_record:
            return ''

        user_property_obj.add_moth_plan_record(now_day)
        #邮件发奖励
        charge_conf = game_config.charge_config
        item_info = charge_conf['charge']['pay_000']
        sid = utils.create_gen_id()
        user_mail = UserMail.hget(self.uid,sid)
        content = u"月卡礼包领取"
        awards = {'1':{"type":diamond,"num":item_info["daily_diamond"]}}
        user_mail.set_mail(from_uid='system',mtype="award",content = content,awards=awards)