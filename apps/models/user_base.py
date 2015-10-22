#-*- coding: utf-8 -*-
import time
import datetime

from apps.common import utils
from apps.oclib.model import UserModel

from apps.models.user_name import UserName
from apps.models.account_mapping import AccountMapping
from apps.models.user_compete import UserCompete

class UserBase(UserModel):
    #"""用户基本信息
    #"""
    pk = 'uid'
    fields = ['uid','baseinfo']
    def __init__(self):
        #"""初始化用户基本信息
        #"""
        self.uid = None
        self.baseinfo = {}
        
    @classmethod
    def get(cls,uid):
        obj = super(UserBase,cls).get(uid)
        return obj
    
    @classmethod
    def get_uid(cls,pid,subarea):
        """获取uid
        """
        oc_uid = AccountMapping.get_user_id(pid, subarea)
        return oc_uid
    
    @classmethod
    def _install(cls,pid,platform,subarea):
        #"""检测安装用户  
        #"""
        uid = cls.get_uid(pid,subarea)
        oc_user = cls.get(uid)
        if oc_user is None:                       
            oc_user = cls._install_new_user(uid,pid,platform,subarea)
        return oc_user
    
    @classmethod
    def _install_new_user(cls,uid,pid,platform,subarea):
        #"""安装新用户，初始化用户及游戏数据
        #"""
        now = int(time.time())
        oc_user = cls.create(uid)
        oc_user.baseinfo["pid"] = pid
        oc_user.baseinfo["username"] = ''
        oc_user.baseinfo["platform"] = platform
        oc_user.baseinfo["subarea"] = subarea
        oc_user.baseinfo["add_time"] = now
        oc_user.baseinfo['bind_time'] = now
        oc_user.put()  
        
        from apps.models.user_property import UserProperty
        from apps.models.user_cards import UserCards        
        UserProperty._install(uid)
        UserCards._install(uid)    
        return oc_user
    
    @classmethod
    def create(cls,uid):
        obj = cls()
        obj.uid = uid
        obj.baseinfo = {
                        'pid':'',#内部32位的唯一id
                        'username':'',# 用户姓名
                        'add_time':int(time.time()),# 安装时间
                        'frozen':False,
                        'frozen_count':0,#已冻结次数
                        'unfroze_time':None,#解冻时间
                        'openid':'',#开放平台有openid
                        'platform':'oc',#开放平台
                        'subarea': '1',  # 分区号
                        'sign':'',#签名
                        'username_cold_time':'',#修改日期冷却时间                            
                        }
        return obj   
    
    @property
    def subarea(self):
        #"""分区号
        #"""
        return str(self.baseinfo.get('subarea', '1'))
    
    @property
    def username(self):
        return self.baseinfo['username']
    
    @property
    def platform(self):
        return self.baseinfo.get('platform','oc')
    
    @property
    def pid(self):
        return self.baseinfo['pid']
    
    @property
    def add_time(self):
        return self.baseinfo['add_time']
    
    @property
    def frozen(self):
        return self.baseinfo['frozen']
        
    @property
    def in_frozen(self):
        #"""是否处于冻结期
        #"""
        if self.frozen:
            return True
        now = int(time.time())
        if self.baseinfo.get('unfroze_time') and self.baseinfo.get('unfroze_time') > now:
            return True
        return False

    @property
    def sign(self):
        if 'sign' not in self.baseinfo:
            self.baseinfo['sign'] = ''
        return self.baseinfo['sign']
         
    @property        
    def account(self):
        #"""用户账户信息
        #"""
        if not hasattr(self, '_account'):
            self._account = AccountMapping.get(self.pid)
        return self._account
    
    @property
    def username_cold_time(self):
        """修改日期冷却时间
        """
        if 'username_cold_time' not in self.baseinfo:
            self.baseinfo['username_cold_time'] = ''
        return self.baseinfo['username_cold_time']       
    
    def froze(self):
        #"""冻结账户，前两次按时间，累计三次之后永久
        #"""
        msg = ''
        if self.in_frozen:
            return ''
        frozen_count = self.baseinfo.get('frozen_count',0)
        if frozen_count:
            self.baseinfo['frozen_count'] += 1
        else:
            self.baseinfo['frozen_count'] = 1
        #首次冻结2天，再次7天，3次永久
        now = datetime.datetime.now()
        if self.baseinfo['frozen_count'] == 1:
            frozen_days = 2
            self.baseinfo['unfroze_time'] = utils.datetime_toTimestamp(now + datetime.timedelta(days=frozen_days))
            msg = utils.get_msg('login','frozen_time', self)
            msg = msg % (frozen_days,utils.timestamp_toString(self.baseinfo['unfroze_time'],'%m.%d %H:%M'),self.uid)
        elif self.baseinfo['frozen_count'] == 2:
            frozen_days = 7
            self.baseinfo['unfroze_time'] = utils.datetime_toTimestamp(now + datetime.timedelta(days=frozen_days))
            msg = utils.get_msg('login','frozen_time', self)
            msg = msg % (frozen_days,utils.timestamp_toString(self.baseinfo['unfroze_time'],'%m.%d %H:%M'),self.uid)
        else:
            self.baseinfo['frozen'] = True
            self.baseinfo['username'] = u'(已冻结)' + self.baseinfo['username']
            msg = utils.get_msg('login','frozen', self) % self.uid
        self.put()
        return msg

    def unfroze(self):
        #"""解冻
        #"""
        if self.in_frozen:
            if self.frozen:
                self.baseinfo['frozen'] = False
                if u'(已冻结)' in self.username:
                    self.baseinfo['username'] = self.username[5:]
            else:
                self.baseinfo['unfroze_time'] = None
            self.put()
        return
    
    @property    
    def property_info(self):
        """用户游戏属性
        """
        if not hasattr(self, '_property_info'):
            from apps.models.user_property import UserProperty
            self._property_info = UserProperty.get(self.uid)
        return self._property_info

    def wrapper_info(self):
        """将自己的信息打包成字典
        """
        now = datetime.datetime.now()
        from apps.models.user_property import UserProperty
        from apps.models.user_dungeon import UserDungeon
        user_property_obj = UserProperty.get(self.uid)
        data = {
            'uid':self.uid,
            'pid':self.pid,
            'subarea':self.subarea,
            'platform':self.platform,
            'username':self.username,
            'exp':user_property_obj.property_info['exp'],  #经验值
            'lv':user_property_obj.property_info['lv'],   #等级
            'diamond':user_property_obj.property_info['diamond'],#付费货币
            'coin':user_property_obj.property_info['coin'], #免费货币
            #'vip_lv':user_property_obj.property_info['vip_lv'],#vip等级 
            'smelting':user_property_obj.property_info.get('smelting',0),#熔炼值  
            'cp':user_property_obj.property_info.get('cp',0),#荣誉   
            'popularity':user_property_obj.property_info.get('popularity',0),#声望
            'max_card_num':user_property_obj.property_info.get("max_card_num",50),#背包栏个数
            'charge_sum':user_property_obj.charge_sum,
            'first_charge':user_property_obj.first_charge,
        }
        user_dungeon_obj = UserDungeon.get_instance(self.uid)
        data["max_floor_id"] = user_dungeon_obj.dungeon_info["max_floor_id"]
        data["last_floor_id"] = user_dungeon_obj.dungeon_info["last"]["floor_id"]
        #八点发奖励
        if now.hour >= 20:
            user_compete_obj = UserCompete.get_instance(self.uid)
            user_compete_obj.send_rank_reward()            
        #邮件的个数
        data["mail_num"] = self.mail_num()
        return data    
    
    def set_name(self,name):
        """设置初始用户名
        """
        if UserName.get(name):
            return False
        try:
            UserName.set_name(self.uid, name)
        except:
            return False
        self.baseinfo['username'] = name
        self.put()
        return True
    
    def mail_num(self):
        """邮件的个数
        """
        from apps.models.user_mail import UserMail
        user_mail_obj = UserMail.hgetall(self.uid) 
        return len(user_mail_obj)
