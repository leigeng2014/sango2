# -*- encoding: utf-8 -*-  
import time
import datetime
from apps.common import utils
from apps.oclib.model import BaseModel
from apps.models.user_mail import UserMail
from apps.config import game_config
from apps.models.guild_user_dungeon import GuildUserDungeon
from apps.models.guild_base import GuildBase

class GuildDungeon(BaseModel):
    """公会战斗
    """
    pk = 'gid'
    fields = ['gid','floor_id','did','round_num','dungeon_record','create_time','hp','total_hp','last_update_time'] 
    def __init__(self, gid = None):
        BaseModel.__init__(self)
        self.gid = gid
        self.floor_id = 1        #当前的战场关卡
        self.did = None          #当前战场的唯一标记
        self.dungeon_record  = []#战斗的记录
        self.create_time = None  #战斗开始时间
        self.hp = 0              #boss的当前hp
        self.total_hp = 5000     #boss的最大hp
        self.last_update_time = 0#上次的刷新时间
        self.round_num = 0       #本次战斗回合数

    @classmethod
    def get(cls, gid):
        obj = super(GuildDungeon, cls).get(gid)
        return obj 
    
    @classmethod
    def get_instance(cls, gid):
        obj = super(GuildDungeon, cls).get(gid)
        if not obj:
            obj = cls._install(gid)
        return obj     
    
    @classmethod
    def _install(cls, gid):
        obj = cls(gid)
        obj.put()
        return obj 
    
    def opendungeon(self):
        #"""开启保卫战
        #"""
        self.did = int(time.time())
        self.create_time = self.did 
        guild_dungeon = game_config.guild_config["guild_dungeon"]
        self.hp = guild_dungeon[str(self.floor_id)]["hp"]
        self.total_hp = guild_dungeon[str(self.floor_id)]["hp"]  
        self.round_num = 0       
        if not self.dungeon_record:
            self.dungeon_record.append(self.did)
        else:
            last_did = self.dungeon_record[-1]
            if utils.timestamp_toDatetime(last_did).date() != datetime.datetime.now().date():
                self.dungeon_record = [self.did]   
        self.put()
        return True 

    def is_boss_dead(self):
        #"""保卫战是否结束  
        if self.hp <= 0:
            return True  
        return False
        
    def update_dungeon(self):
        """更新战况(每3分钟刷新一下)
        """
        if self.is_boss_dead():
            return False
        
        now = int(time.time())
        if now - self.create_time > 3600 * 4:
            now = self.create_time + 3600 * 4            
        num = (now - self.last_update_time) / 300
        if num < 1:
            return False
        
        #更新一下最后一次的刷新时间
        self.last_update_time = int(time.time())
        self.put()
        
        #计算伤害   
        last_dungeon_uid = None     #最后一击的人
        for _ in range(num): 
            last_dungeon_uid = self.__round_dungeon()
            self.round_num += 1
            self.put()
            if last_dungeon_uid:
                break
  
        #如果boss被打死，发奖励并且给最后一击的人发奖励  
        if last_dungeon_uid:
            now = int(time.time())
            if self.round_num <= 12:
                self.floor_id += 1
            self.give_award(True,last_dungeon_uid)
            self.put()
            return True

        #判断时间是否超过4个小时，如果超过，说明失败了
        if now - self.create_time >= 4*3600:
            self.give_award(False) 
            if self.floor_id > 1:
                self.floor_id -= 1 
            self.hp = 0                
            self.put()
            return True
        return True

    def __round_dungeon(self):
        """一个回合的结算
        """
        last_dungeon_uid = None    
        guild_base_obj = GuildBase.get_instance(self.gid)
        for uid in guild_base_obj.all_member:
            guild_user_dungeon_obj = GuildUserDungeon.get_instance(uid)
            if guild_user_dungeon_obj.did == self.did:
                damage = 100 + int(guild_user_dungeon_obj.inspire_num *  100 * 0.1)
                guild_user_dungeon_obj.damage += damage   #自己的伤害总和
                guild_user_dungeon_obj.put() 
                self.hp -= damage                         #扣掉boss的血
                self.put()
                if self.is_boss_dead() is True:
                    last_dungeon_uid = uid
                    break
        return last_dungeon_uid
                    
    def give_award(self,is_win,last_dungeon_uid=None):
        """给奖励
        """
        guild_base_obj = GuildBase.get(self.gid)
        guild_dungeon = game_config.guild_config["guild_dungeon"]
        exp = guild_dungeon[str(self.floor_id)]["exp"]
        gcontribution = guild_dungeon[str(self.floor_id)]["exp"]
        lv = guild_dungeon[str(self.floor_id)]["lv"]  
                      
        #公会加经验
        guild_base_obj.add_gexp(exp)
        
        #会员发奖励,如果输了，奖励减半
        member = []
        for uid in guild_base_obj.all_member:
            guild_user_dungeon_obj = GuildUserDungeon.get_instance(uid)
            if guild_user_dungeon_obj.did == self.did:
                member.append((uid,guild_user_dungeon_obj.damage))
        member = sorted(member,key=lambda x:x[1])
        
        award_config = {1:0.2,2:0.15,3:0.12,4:0.10,5:0.09,6:0.08,7:0.07,8:0.06,9:0.05,10:0.04,11:0.01}
        rank = 0
        for obj in member:            
            uid = obj[0]            
            rank += 1
            sid = utils.create_gen_id()
            user_mail = UserMail.hget(uid,sid)
            content = u"打败魔兽，获得奖励"            
            award_rate = 0.01 if is_win else 0.005
            if rank in award_config:
                award_rate = award_config[rank]                
            awards = {}
            awards['1'] = {'type':'gcontribution','num':int(gcontribution*award_rate)}
            #前3名发强化精华
            if rank < 4:
                num = int(0.2*lv) if is_win else int(0.1*lv)
                awards['2'] = { 'type':'item','num':num,'id':'it_04101'}
            user_mail.set_mail(from_uid='system',mtype="award",content = content,awards = awards)
            
        if is_win and last_dungeon_uid:
            sid = utils.create_gen_id()
            user_mail = UserMail.hget(last_dungeon_uid,sid)
            content = u"公会boss战斗，最后一击奖励"
            user_mail.set_mail(from_uid='system',mtype="award",content = content,awards = awards) 
            
            #称号     
            from apps.models.user_title import UserTitle
            user_title_obj = UserTitle.get_instance(last_dungeon_uid)
            user_title_obj.set_title('6')    
        return True