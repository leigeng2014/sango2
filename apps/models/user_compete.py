#-*- coding: utf-8 -*-
import time
import copy
import random
import datetime
from apps.common import utils
from apps.oclib.model import UserModel
from apps.config import game_config
from apps.models.virtual.card_npc import CardNpc
from apps.models.compete_rank import get_compete_rank
from apps.models.user_equipments import UserEquipments
from apps.models.user_cards import UserCards
from apps.models.user_compete_record import UserCompeteRecord
from apps.models.user_mail import UserMail

class UserCompete(UserModel):
    """用户竞技信息
    """    
    pk = 'uid'
    fields = ['uid','compete_info']
    def __init__(self,uid = None):
        self.uid = uid  
        self.compete_info = {} 

    @classmethod
    def get(cls,uid):
        obj = super(UserCompete,cls).get(uid)
        return obj
    
    @classmethod
    def get_instance(cls,uid):
        obj = super(UserCompete,cls).get(uid)
        if obj is None:
            obj = cls._install(uid)
            return obj
        return obj
    
    @classmethod
    def _install(cls,uid):
        obj = cls(uid)
        obj.compete_info = {
            'buy_num':0,    #今天购买的次数
            'compete_num':5,#今天可以挑战次数
            'total_num':0,  #历史挑战总次数
            'success_num':0,#历史挑战成功次数
            'last_compete_time':int(time.time()),
            'enemy_info':{},
            'last_reward_date':'',#上一次领奖的时间
            'last_fail_time':'',#上次失败的时间
        }
        obj.put()        
        return obj 
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base

    @property
    def last_fail_time(self):
        """上次失败的时间(为了记录冷却时间)
        """
        if 'last_fail_time' not in self.compete_info:
            self.compete_info["last_fail_time"] = ''
            self.put()
        return self.compete_info["last_fail_time"]
    
    @property
    def last_reward_date(self):
        """上次发奖励的时间
        """ 
        if self.compete_info["last_reward_date"] == '':
            hour = datetime.datetime.now().hour
            if hour >= 20:
                last_reward_date = datetime.datetime.now()
            else:
                last_reward_date = datetime.datetime.now() - datetime.timedelta(days=1)
            self.compete_info["last_reward_date"] = str(last_reward_date.date())
            self.put()
        return self.compete_info["last_reward_date"]
    
    @property
    def my_rank(self):
        """我的排名
        """
        rank = 0
        compete_rank_obj = get_compete_rank(self.user_base.subarea)
        #如果自己是第一个人，则排名为2001
        count = compete_rank_obj.count()
        if count == 0:
            rank = 2001
            compete_rank_obj.set(self.uid,2001)
        #如果自己不在排名中，则读取最后一名。如果最后一名+5小于2001，则排名为2001
        #如果最后一名+5大于2001，则排名为最后一名+5
        else:
            rank = compete_rank_obj.score(self.uid)
            if not rank:                
                last_rank = int(compete_rank_obj.get(count=1)[0][1])
                if last_rank < 1996:  
                    rank = 2001
                    compete_rank_obj.set(self.uid,rank)
                else:                    
                    rank = last_rank + 5
                    compete_rank_obj.set(self.uid,rank)
            else: 
                rank = compete_rank_obj.score(self.uid)
        return int(rank)
    
    @property
    def get_my_reward(self):
        """我的竞技奖励
        """
        return self.__get_rank_reward(self.my_rank)

    def send_rank_reward(self):
        """每日竞技排行奖励
        """        
        now = datetime.datetime.now()
        #如果今天领过奖励就返回空
        if self.last_reward_date >= str(now.date()):
            return ''
        
        #要发奖的日期列表
        reward_date_list = []
        last_reward_date = self.last_reward_date + ' 20:00:00'
        last_reward_date = datetime.datetime.strptime(last_reward_date,'%Y-%m-%d %H:%M:%S')
        time_delta = (now - last_reward_date).days
        if time_delta > 30:
            time_delta = 30
        for i in range(time_delta):
            create_time = last_reward_date + datetime.timedelta(days=i+1)
            reward_date_list.append(create_time)   
        #如果reward_date_list为空,则返回
        if len(reward_date_list) == 0:
            return ''
            
        #竞技记录列表  
        record_detail = []
        compete_record_obj = UserCompeteRecord.hgetall(self.uid)
        if compete_record_obj:
            compete_record_list = sorted(compete_record_obj.items(),key = lambda x:x[1]["record_info"]["create_time"])
            i = 1
            for obj in compete_record_list:
                record_info = obj[1]["record_info"]
                create_time = record_info["create_time"][:19]
                end_rank = record_info["end_rank"]
                create_time = datetime.datetime.strptime(create_time,'%Y-%m-%d %H:%M:%S')
                record_detail.append((create_time,end_rank))                 
        record_detail.append((now,self.my_rank))#把当前的排行加入记录列表  
        #########最终的排名发奖信息（待优化）#########
        result = {}
        for i in reward_date_list:
            if len(record_detail) == 1:
                result[i] = record_detail[0][1]
            else:    
                for j in record_detail:            
                    if j[0] > i:
                        break
                    result[i] = j[1]
                    
        result = sorted(result.items(),key=lambda x:x[0])
        ################################
        #把奖励发到邮件中
        for obj in result:
            rank = obj[1]
            if not rank:
                continue
            mid = utils.create_gen_id()
            user_mail = UserMail.hget(self.uid,mid)
            reward = self.__get_rank_reward(rank)
            awards = { 
                '1':{
                    'type':'diamond', #物品类型
                    'num':reward["diamond"], #数量
                },
                '2':{
                    'type':'cp', #物品类型
                    'num':reward["cp"], #数量
                },
            }
            content = "恭喜您成功守卫了您竞技[%s]的排名 。您的奖励：[获得%s钻石] [获得%s荣誉]" % \
                                 (rank,reward["diamond"],reward["cp"])
            create_time = obj[0].strftime('%Y-%m-%d %H:%M:%S')
            user_mail.set_mail(mtype="award",content=content,awards=awards,create_time=create_time)
        self.compete_info["last_reward_date"] = str(now.date())
        self.put()  
                   
    def get_compete_user_obj(self,compete_dict):
        """获取竞技对手的对象
        """
        from apps.models.virtual.monster import Monster
        obj = Monster.get_compete(compete_dict)
        return obj
 
    def get_my_enemy(self):
        """我的3个竞技对手
        """
        result = []
        my_rank = self.my_rank
        #第一名,显示2,3,4
        if my_rank == 1:
            first_rank = 2
            second_rank = 3
            third_rank = 4
        #第二名,显示1,3,4
        elif my_rank == 2:
            first_rank = 1
            second_rank = 3
            third_rank = 4
        #第三名,显示1,2,4
        elif my_rank == 3:
            first_rank = 1
            second_rank = 2
            third_rank = 4
        #其他的根据规则
        else:
            first_rank = random.randint(int(my_rank*0.25),int(my_rank*0.5)-1) #25%<=第一位置<50%
            second_rank = random.randint(int(my_rank*0.5),int(my_rank*0.95)-1) #50%<=第二位置<95%
            third_rank = random.randint(int(my_rank*0.95),int(my_rank)-1) #95%<=第三位置<100%
        
        for user_rank in [first_rank,second_rank,third_rank]:
            data = {}
            #根据我排名算出，对应的奖励区间
            rank_conf = copy.deepcopy(game_config.compete_config["rank_conf"])
            rank_conf_sort = sorted(rank_conf.items(),key=lambda x:int(x[0]))
            reward_rank = 1
            if str(user_rank) in rank_conf:
                reward_rank = user_rank
            else:
                for ran in rank_conf_sort:
                    reward_rank = int(ran[0])
                    if int(ran[0]) > user_rank:
                        break
            cp_base = rank_conf[str(reward_rank)]["cp_base"]
            diamond_base = rank_conf[str(reward_rank)]["diamond_base"]
            
            #根据排名，求出对应的uid，uid为空时，读取npc的数据
            compete_rank_obj = get_compete_rank(self.user_base.subarea)
            uid = compete_rank_obj.get_name_by_score(user_rank,user_rank) 
            if not uid:
                npc_id = rank_conf[str(reward_rank)]["npcId"]
                npc_lv_base = rank_conf[str(reward_rank)]["npc_lv_base"]
                npc_lv_growth = rank_conf[str(reward_rank)]["npc_lv_growth"]
                npc_lv =  int(npc_lv_base + (reward_rank - user_rank)*npc_lv_growth)
                compete_npc_config = game_config.compete_npc_config
                #npc前20名读取特定配置
                if user_rank > 20:
                    npc_name = utils.random_choice(compete_npc_config["common_npcName"],1)[0]
                    npc_icon = utils.random_choice(compete_npc_config["common_npcIcon"],1)[0]
                    common_npc_config = compete_npc_config["common_npc"]                    
                    npc_config = common_npc_config[npc_id]
                    npc_card_obj = CardNpc.get(npc_icon,npc_lv,npc_config)  
                    
                    data.update({"rank":user_rank,"uid":"npc",\
                                 "cid":npc_icon,"name":npc_name,\
                                 "cp":cp_base,"diamond":diamond_base}) 
                    npc_card_dict = copy.deepcopy(npc_card_obj.__dict__)
                    npc_card_dict.pop("card_detail")
                    npc_card_dict.pop("card_category_config")
                    npc_card_dict.pop("subarea")
                    data.update(npc_card_dict)
                else:
                    top_npc_config = compete_npc_config["top_npc"][npc_id]
                    npc_card_obj = CardNpc.get(top_npc_config["icon"],npc_lv,top_npc_config)
                    data.update({"rank":user_rank,"uid":"npc",\
                                 "cid":top_npc_config["icon"],\
                                 "name":top_npc_config["name"],\
                                 "cp":cp_base,"diamond":diamond_base}) 
                    npc_card_dict = copy.deepcopy(npc_card_obj.__dict__)
                    npc_card_dict.pop("card_detail")
                    npc_card_dict.pop("card_category_config")
                    npc_card_dict.pop("subarea")
                    data.update(npc_card_dict)
            else:
                uid = uid[0]
                user_cards_obj = UserCards.get(uid)
                user_equipments_obj = UserEquipments.get_instance(uid)
                equipments = {}
                for _,v in user_cards_obj.equipments.items():
                    if v:
                        equipments[v] = user_equipments_obj.equipments[v]
                user_base_obj  = user_cards_obj.user_base
                lv = user_base_obj.property_info.property_info["lv"]
                cid = user_cards_obj.cid
                user_card_dict = user_cards_obj.card_obj().__dict__
                user_card_dict["skill_list"] = user_cards_obj.skill_defensive
                user_card_dict.pop("card_detail")
                user_card_dict.pop("card_category_config")
                user_card_dict.pop("subarea")                
                data.update(user_card_dict)
                name = user_base_obj.baseinfo["username"]
                data.update({"rank":user_rank,"uid":uid,"lv":lv,"cid":cid,"name":name,\
                             'user_equipments':user_cards_obj.equipments,'equipments':equipments,\
                             "cp":cp_base,"diamond":diamond_base,'force':user_cards_obj.force})
                team = {}
                team['teams_info'] = {}
                team['develop_info'] = {}
                team['teams_equipments'] = {}
                from apps.models.user_teams import UserTeams
                user_teams_obj = UserTeams.get_instance(uid) 
                if user_teams_obj.team:  
                    team['teams_info'] = user_teams_obj.teams_info[str(user_teams_obj.team[0])]
                    team['develop_info'] = user_teams_obj.develop_info[str(user_teams_obj.team[0])]
                    equipments = {}
                    for _,v in team['teams_info']["equipments"].items():
                        if v:
                            equipments[v] = user_equipments_obj.equipments[v]
                            ############此处以后要去掉###############
                            if 'star' not in equipments[v]:
                                equipments[v]['star'] = 0
                                equipments[v]['special_attr'] = {}
                    team['teams_equipments'] = equipments
                data.update({"team":team})
            result.append(data)
        return result
    
    def __get_rank_reward(self,user_rank):
        """获取指定排名的奖励
        """
        result = {}
        reward_rank = 1
        rank_conf = copy.deepcopy(game_config.compete_config["rank_conf"])
        rank_conf_sort = sorted(rank_conf.items(),key=lambda x:int(x[0]))
        if str(user_rank) in rank_conf:
            reward_rank = user_rank
        else:
            for ran in rank_conf_sort:
                reward_rank = int(ran[0])
                if int(ran[0]) > user_rank: 
                    break
            
        cp_base = rank_conf[str(reward_rank)]["cp_base"]
        cp_growth = rank_conf[str(reward_rank)]["cp_growth"]
        diamond_base = rank_conf[str(reward_rank)]["diamond_base"]
        diamond_growth = rank_conf[str(reward_rank)]["diamond_growth"]
        
        user_base_obj  = self.user_base
        lv = user_base_obj.property_info.property_info["lv"]
        cp = int(cp_base + (lv - 1)*cp_growth)
        diamond = int(diamond_base + (lv-1)*diamond_growth)   
        result["cp"] = cp
        result["diamond"] = diamond
        return result