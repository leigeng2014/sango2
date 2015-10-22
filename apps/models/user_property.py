#-*- coding: utf-8 -*-
from apps.oclib.model import UserModel
from apps.config import game_config
from apps.models.user_teams import UserTeams
from apps.models.rank import Rank,update_force_rank

class UserProperty(UserModel):
    """用户游戏内部基本信息
    """
    pk = 'uid'
    fields = ['uid','property_info']
    def __init__(self):
        #"""初始化用户游戏内部基本信息
        #"""        
        self.uid = ''
        self.property_info = {
            'exp':0,#经验值
            'lv':1,
            'diamond':0,
            'coin':0,
            'max_card_num':0, 
            'vip_lv':0,   
            'cp':0,     #荣誉
            'popularity':0,#声望  
            'smelting':0,  #熔炼值 
            'charge_sum':0,#充值的人民币数  
            'newbie':True,
            'newbie_step':0,
            'month_plan_end_time':'',
            'month_plan_record':[],
            'first_charge':True,
        }
        
    @classmethod
    def get(cls,uid):
        obj = super(UserProperty,cls).get(uid)
        return obj 
    
    @classmethod
    def _install(cls,uid):
        obj = cls()
        obj.uid = uid
        system_config = game_config.system_config
        obj.property_info["max_card_num"] = system_config["equipNum_limit"]
        obj.put()     
        return obj
       
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    @property
    def newbie(self):
        return self.property_info.get("newbie",False)  
    
    @property
    def newbie_step(self):        
        return self.property_info.get("newbie_step",0)  
      
    @property
    def coin(self):        
        return self.property_info.get("coin")
           
    @property
    def charge_sum(self):
        """充值的money(人民币)
        """
        if not self.property_info.get('charge_sum'):
            self.property_info["charge_sum"] = 0
            self.put()
        return self.property_info["charge_sum"]
    
    @property
    def vip_lv(self):
        """vip等级
        """ 
        if not hasattr(self, '_vip_lv'):
            result = 0 
            vip_config = game_config.vip_config
            vip_list = sorted(vip_config.items(),key=lambda x:x[1]["charge"])
            for k,v in vip_list:
                if (self.charge_sum * 10) < v["charge"]:
                    break
                result = k
            self._vip_lv = result        
        return self._vip_lv
    
    @property
    def lv(self):
        """最大背包数
        """
        return self.property_info["lv"]
    
    @property
    def max_card_num(self):
        """最大背包数
        """
        return self.property_info["max_card_num"]

    @property
    def first_charge(self):
        if 'first_charge' not in self.property_info:
            self.property_info["first_charge"] = True
            self.put()
        return self.property_info["first_charge"]

    @property
    def month_plan_end_time(self):
        """月卡结束时间
        """
        if 'month_plan_end_time' not in self.property_info:
            self.property_info["month_plan_end_time"] = ''
            self.put()
        return self.property_info["month_plan_end_time"]

    @property
    def month_plan_record(self):
        """月卡领取记录
        """
        if 'month_plan_record' not in self.property_info:
            self.property_info["month_plan_record"] = []
            self.put()
        return self.property_info["month_plan_record"]
  
    def add_month_plan_record(self,date):
        """领取月卡记录
        """
        self.property_info["month_plan_record"].append(date)
        if len(self.property_info["month_plan_record"]) > 10:
            self.property_info["month_plan_record"].pop(0)
        self.put()
        return True 
    
    def add_diamond(self,diamond,where=None):
        """增加用户的钻石
        """
        self.property_info['diamond'] += diamond
        self.put()
        
    def is_diamond_enough(self,diamond):
        """检查用户的钻石是否足够
        """
        return self.property_info['diamond'] >= abs(diamond)
    
    def minus_diamond(self,diamond,where=None):
        """减少diamond数量
        """
        diamond = abs(diamond)
        if self.is_diamond_enough(diamond):
            self.property_info['diamond'] -= diamond
            self.put()
            return True
        else:
            return False    
        
    def add_coin(self,coin,where=None):
        """增加用户的金币
        """
        self.property_info['coin'] += coin
        self.put()
        
    def is_coin_enough(self,coin):
        """检查金币是否充足
        """
        return self.property_info['coin'] >= abs(coin)
    
    def minus_coin(self,coin,where=None):
        """消耗金币
        """
        coin = abs(coin)
        if self.is_coin_enough(coin):
            self.property_info['coin'] -= coin
            self.put()
            return True
        else:
            return False

    def add_popularity(self,popularity,where=None):
        """增加用户的声望
        """
        self.property_info['popularity'] += popularity
        self.put()
        
    def is_popularity_enough(self,popularity):
        """检查声望是否充足
        """
        return self.property_info['popularity'] >= abs(popularity)
    
    def minus_popularity(self,popularity,where=None):
        """消耗声望
        """
        popularity = abs(popularity)
        if self.is_popularity_enough(popularity):
            self.property_info['popularity'] -= popularity
            self.put()
            return True
        else:
            return False
        
    def add_smelting(self,smelting,where=None):
        """增加用户的熔炼值
        """
        self.property_info['smelting'] += smelting
        self.put()
        
    def is_smelting_enough(self,smelting):
        """检查熔炼值是否充足
        """
        return self.property_info['smelting'] >= abs(smelting)
    
    def minus_smelting(self,smelting,where=None):
        """消耗熔炼值
        """
        smelting = abs(smelting)
        if self.is_smelting_enough(smelting):
            self.property_info['smelting'] -= smelting
            self.put()
            return True
        else:
            return False
         
    def add_cp(self,cp,where=None):
        """增加用户的荣誉
        """
        self.property_info.setdefault('cp',0)
        self.property_info['cp'] += cp
        self.put()
        
    def add_smelting(self,smelting,where=None):
        """增加用户的金币
        """
        self.property_info.setdefault('smelting',0)
        self.property_info['smelting'] += smelting
        self.put()

    def add_exp(self,exp, where = None):
        """增加经验
        """
        lv_up_fg = False
        from apps.models.user_cards import UserCards   
        user_cards_obj = UserCards.get(self.uid)
        cid = user_cards_obj.cid
        card_config = game_config.card_config[cid] 
        exp_type = card_config['exp_type']        
        card_level_config = game_config.card_level_config['exp_type'][exp_type]
        max_lv = max([int(i) for i in card_level_config.keys()])
        if self.property_info['lv'] < max_lv:
            new_lv = self.property_info['lv']
            self.property_info['exp'] = self.property_info['exp'] + exp
            exp_rank_obj = Rank(self.user_base.subarea,'exp_rank')
            exp_rank_obj.set(self.uid,self.property_info['exp']) 
            for next_lv in range(self.property_info['lv'] + 1,max_lv + 1):
                next_lv_exp = card_level_config[str(next_lv)]
                if self.property_info['exp'] >= next_lv_exp:
                    lv_up_fg = True
                    new_lv = next_lv
                else:
                    break
       
        if lv_up_fg:
            update_force_rank(self.uid)
            self.property_info['lv'] = new_lv
            #检查是否需要开启佣兵
            teams_lock = game_config.card_level_config['team_unlock']
            user_teams_obj = UserTeams.get_instance(self.uid)
            for k_,v_ in teams_lock.items():
                if (int(new_lv)  >= int(v_)) and (str(k_) not in user_teams_obj.teams_info):
                    user_teams_obj.add_team(k_)
        self.put()
        return lv_up_fg

    def add_charge_sum(self,charge_sum,where=None):
        """增加用户的金币
        """
        self.property_info['charge_sum'] += charge_sum
        self.put()
        
    def give_award(self,award):
        """给奖励
        """
        from apps.models.guild_user import GuildUser
        for key in award:
            if key == 'exp':
                self.add_exp(award[key])
            elif key == 'coin':
                self.add_coin(award[key])
            elif key == 'diamond':
                self.add_diamond(award[key])
            elif key == 'gcontribution':
                guild_user_obj = GuildUser.get_instance(self.uid)
                guild_user_obj.add_gcontribution(award[key])
            elif key == 'gcoin':              
                guild_user_obj = GuildUser.get_instance(self.uid)
                guild_user_obj.add_contribute_gcoin(award[key])
            elif key == "popularity":
                self.property_info["popularity"] += award[key]
                self.put()