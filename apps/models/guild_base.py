#-*- coding: utf-8 -*-  
from apps.oclib.model import BaseModel
from apps.config import game_config
from apps.models.rank import Rank
from apps.models.guild_name import GuildName

class GuildBase(BaseModel):
    #"""公会
    # 公会名称，公会宣言，公会会长，公会副会长，公会成员,公会粮饷
    # 公会经验，公会等级
    #"""
    pk = 'gid'
    fields = ['gid','gname','guildbase_info'] 
    def __init__(self,gid = None):
        self.gid = gid
        self.gname = "" #公会名称
        self.guildbase_info = {
                                 "gleader":"",       #公会会长
                                 "gsecondleader":[], #公会副会长
                                 "gmember":[],       #公会成员
                                 "gexp":0,           #公会gexp
                                 "gcoin":0,          #公会资金 
                                 "lv":1,         #公会等级
                                 "create_uid":'',    #创建者
                                 "gnotice":'',  #公会公告
                                 "condition":0,  #入会条件
                                 "sk_lv":0,       #技能学院等级
                                 "shop_lv":0,      #贡献商店
                                 "subarea":'10', #分区
                              }
    
    @classmethod
    def get_instance(cls, gid):
        obj = super(GuildBase,cls).get(gid)
        if obj is None:
            obj = cls._install(gid)
        return obj 

    @classmethod
    def get(cls, gid):
        obj = super(GuildBase,cls).get(gid)
        return obj 
        
    @classmethod
    def _install(cls, gid):
        obj = cls(gid)
        obj.put()
        return obj 
    
    @property
    def gleader(self):
        return self.guildbase_info.get("gleader", None) 
    
    @property
    def gsecondleader(self):
        return self.guildbase_info.get("gsecondleader", []) 
    
    @property
    def create_uid(self):
        return self.guildbase_info.get("create_uid", self.guildbase_info["gleader"]) 
    
    @property
    def gmember(self):
        return self.guildbase_info.get("gmember", [])
     
    @property
    def all_member(self):
        member = [self.gleader] + self.gsecondleader + self.gmember        
        return [ m for m in member if m] 
    
    @property
    def gnotice(self):
        return self.guildbase_info.get("gnotice",'')
    
    @property
    def total_num(self):
        return len(self.all_member) 
    
    @property
    def gexp(self):
        return self.guildbase_info.get("gexp",0)

    @property
    def lv(self):
        return self.guildbase_info.get("lv", 1)
    
    @property
    def condition(self):
        return self.guildbase_info.get("condition",0)
    
    @property
    def max_num(self):
        """当前公会成员的上限
        """
        return 20 + (self.lv-1)*2
    
    @property
    def subarea(self):
        """分区
        """
        if 'subarea' not in self.guildbase_info:
            from apps.models.user_base import UserBase
            user_base = UserBase.get(self.gleader)
            self.guildbase_info['subarea'] = user_base.subarea
            self.put()            
        return  self.guildbase_info['subarea']
    
    def add_gexp(self,gexp):
        """加公会经验
        """
        config = game_config.guild_config["gexp"]
        max_lv = max([int(i) for i in config.keys()])
        new_lv = self.lv
        new_gexp = self.gexp + gexp
        if new_gexp >= config[str(max_lv)]:
            new_gexp = config[str(max_lv)]
            new_lv = max_lv
        else: 
            for lv in range(new_lv+1,max_lv+1):
                next_lv_gexp = config[str(lv)]
                if new_gexp >= next_lv_gexp:
                    new_lv = lv
                else:
                    break
        #公会等级排行榜
        guild_rank_obj = Rank(self.subarea,'guild_rank')
        guild_rank_obj.set(self.gid,new_gexp)
        self.guildbase_info["lv"] = new_lv
        self.guildbase_info["gexp"] = new_gexp
        self.put()
        
    @property    
    def next_lv_gexp(self):
        """加公会经验
        """
        config = game_config.guild_config["gexp"]
        gexp = 99999999
        next_lv = str(self.lv+1)
        if next_lv in config:
            gexp = config[next_lv]
        return gexp
    
    @property
    def sk_lv(self):
        """技能等级
        """
        if "sk_lv" not in self.guildbase_info:
            self.guildbase_info["sk_lv"] = 0
            self.put()
        return self.guildbase_info["sk_lv"]
    
    @property
    def shop_lv(self):
        """技能等级
        """
        if "shop_lv" not in self.guildbase_info:
            self.guildbase_info["shop_lv"] = 0
            self.put()
        return self.guildbase_info["shop_lv"]
    
    @property
    def gcoin(self):
        """公会资金
        """
        if "gcoin" not in self.guildbase_info:
            self.guildbase_info["gcoin"] = 0
            self.put()
        return self.guildbase_info["gcoin"]

    def add_gcoin(self,gcoin):
        """加公会资金
        """
        self.guildbase_info["gcoin"] += gcoin
        self.put()
        
    def set_name(self,name):
        """设置初始用户名
        """
        if GuildName.get(name):
            return False
        try:
            GuildName.set_name(self.uid, name)
        except:
            return False
        self.gname = name
        self.put()
        return True