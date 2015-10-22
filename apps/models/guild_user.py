# -*- encoding: utf-8 -*-  
import time
import datetime
from apps.common import utils
from apps.oclib.model import UserModel

class GuildUser(UserModel):
    #"""个人公会信息
    #"""
    pk = 'uid'
    fields = ['uid','guilduser_info'] 
    def __init__(self, uid = None):
        #"""gid(所属公会id)
        #"""
        self.uid = uid
        self.guilduser_info = {"gid":None,                           #公会id
                               "name":"",                            #公会名字
                               "contribute_gcoin":0,                 #捐献的总资金  
                               "gcontribution":50000,                #总贡献
                               "remain_gcontribution":0,             #当前的贡献
                               "quit_guild_time":'',                 #退出公会的时间
                               "last_sign_time":'',                  #上次签到的日期
                               "last_contribution_time":'',          #上次捐献的日期
                               "sign_num":0,                         #签到次数
                               "buy_record":{'1':0,'2':0,'3':0,'4':0,'5':0,'6':0},#购买次数 
                               "learn_skill_record":[],
                               "refresh_shop_time":int(time.time()), #商店刷新的时间
                               "is_self_quit":0,                     #是否是自己退出公会 1代表自己退出，2代表被踢的
                               }
    @classmethod
    def get(cls, uid):
        obj = super(GuildUser, cls).get(uid)
        return obj
        
    @classmethod
    def get_instance(cls, uid):
        obj = super(GuildUser, cls).get(uid)
        if obj is None:
            obj = cls._install(uid)   
        return obj
     
    @classmethod
    def _install(cls, uid):
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
    def gid(self):
        return self.guilduser_info.get("gid", None)
    
    @property
    def gcontribution(self):
        return self.guilduser_info.get("gcontribution", 0) 
    
    @property
    def remain_gcontribution(self):
        if "remain_gcontribution" not in self.guilduser_info:
            self.guilduser_info["remain_gcontribution"] = self.gcontribution
            self.put()
        return self.guilduser_info.get("remain_gcontribution", 0) 
    
    def is_guild_member(self):
        #"""判断是否是公会的会员
        #"""
        return self.guilduser_info.get("gid", None) is not None
    
    @property
    def name(self):
        """公会的名字
        """
        return self.guilduser_info.get("name",'')
    
    @property
    def quit_guild_time(self):
        """退出上个公会的时间
        """
        return self.guilduser_info.get("quit_guild_time",'')
    
    @property
    def last_sign_time(self):
        """最后一次签到的时间
        """
        return self.guilduser_info.get("last_sign_time",'')
    
    @property
    def last_contribution_time(self):
        """最后一次捐献的时间
        """
        if "last_contribution_time" not in self.guilduser_info:
            self.guilduser_info["last_contribution_time"] = datetime.datetime.now().date()
            self.put()
        return self.guilduser_info.get("last_contribution_time") 
    
    @property
    def sign_num(self):
        """公会签到次数
        """    
        if "sign_num" not in self.guilduser_info:
            self.guilduser_info["sign_num"] = 0
            self.put()
        return self.guilduser_info.get("sign_num",'') 
    
    @property
    def refresh_shop_time(self):
        """刷新商店购买记录的时间
        """ 
        if "refresh_shop_time" not in self.guilduser_info:
            self.guilduser_info["refresh_shop_time"] = int(time.time())
            self.put()
        return self.guilduser_info.get("refresh_shop_time",'')
    
    @property
    def buy_record(self):
        """购买记录
        """
        if "buy_record" not in self.guilduser_info:
            self.guilduser_info["buy_record"] = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0}
            self.put()
        return self.guilduser_info.get("buy_record")
    
    @property
    def position(self):
        """在公会中的职位
        """
        from apps.models.guild_base import GuildBase
        guild_base_obj = GuildBase.get_instance(self.gid)
        position = "common"
        if self.uid in [guild_base_obj.gleader]:
            position = "leader"            
        elif self.uid  in guild_base_obj.gsecondleader:
            position = "secondleader"
        return position
    
    @property
    def is_self_quit(self):
        """是否是自己退出的公会
        """
        if "is_self_quit" not in self.guilduser_info:
            self.guilduser_info["is_self_quit"] = 0
            self.put()
        return self.guilduser_info.get("is_self_quit")
    
    @property
    def learn_skill_record(self):
        """技能学习记录
        """
        if "learn_skill_record" not in self.guilduser_info:
            self.guilduser_info["learn_skill_record"] = []
            self.put()
        return self.guilduser_info.get("learn_skill_record")
    
    @property
    def contribute_gcoin(self):
        """捐献的公会资金
        """
        if "contribute_gcoin" not in self.guilduser_info:
            self.guilduser_info["contribute_gcoin"] = 0
            self.put()
        return self.guilduser_info.get("contribute_gcoin")        
        
    def add_gcontribution(self,gcontribution):
        """加贡献
        """
        self.guilduser_info["gcontribution"] += gcontribution
        self.guilduser_info["remain_gcontribution"] += gcontribution
        self.put()
        
    def minus_gcontribution(self,gcontribution):
        """减少贡献
        """        
        if self.is_gcontribution_enough(gcontribution):
            self.guilduser_info["remain_gcontribution"] -= gcontribution
            self.put()
            return True
        return False
        
    def is_gcontribution_enough(self,gcontribution):
        """检查贡献是否充足
        """
        return self.remain_gcontribution >= abs(gcontribution)
    
    def refresh_buy_record(self):
        """刷新商品购买记录
        """
        now = datetime.datetime.now().date()            
        refresh_shop_time = utils.timestamp_toDatetime(self.refresh_shop_time).date()
        weekday = refresh_shop_time.weekday()
        end_date = refresh_shop_time + datetime.timedelta(days = 7 - weekday)

        if now < end_date:
            return False

        self.guilduser_info["buy_record"] = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0} 
        self.guilduser_info["refresh_shop_time"] = int(time.time())         
        self.put()
        return True
    
    def add_contribute_gcoin(self,gcoin):
        """加公会资金
        """
        self.guilduser_info["contribute_gcoin"] += gcoin
        self.put()  
        from apps.models.guild_base import GuildBase
        guild_base_obj = GuildBase.get(self.guilduser_info["gid"])
        guild_base_obj.add_gcoin(gcoin)  