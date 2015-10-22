#-*- coding: utf-8 -*-
import time
from apps.common import utils
from apps.oclib.model import UserModel
from apps.config import game_config
from apps.models.user_property import UserProperty

class  UserDungeon(UserModel):
    #"""用户的战场信息
    #"""
    pk = 'uid'
    fields = ['uid','dungeon_info']
    
    def __init__(self, uid=None):
        self.uid = uid
        self.dungeon_info = {}
                                    
    @classmethod
    def get(cls, uid):
        #"""获取类对象
        #"""
        obj = super(UserDungeon, cls).get(uid)
        return obj
        
    @classmethod
    def get_instance(cls, uid):
        #"""获取类对象
        #"""
        obj = super(UserDungeon, cls).get(uid)
        if obj is None:
            obj = cls._install(uid)
           
        return obj    
    
    @classmethod
    def _install(cls, uid):
        #"""生成类对象
        #"""
        obj = cls(uid)
        obj.dungeon_info = {
              'max_floor_id':1,
              'last':{
                      'floor_id':1,#最后一次战场的战场id
                      'enter_date':int(time.time()),#最后一次进入的时间
                      'round_num':0, #本次战斗的回合数
              },
              'sucess_rate_record':[70,70,70,70],#记录当前战斗最近5次的胜率，刚进本战场默认5个70
              'dungeon_date_record':[],#战斗时间记录
              'dun_boss_num':3,     #每天可以免费挑战boss的次数
              'buy_dun_boss_num':0, #今天购买的挑战boss的次数
              'buy_fast_dun_num':0, #今天购买的快速战斗次数
              'buy_special_dun_num':0, #今天购买的精英战斗次数
              'tutorial_dun_num':0, #新手战斗的次数
              'dun_special_num':3,  #每天可以免费挑战精英战场的次数
              'max_special_floor_id':0,#精英关卡最大id
              'max_expedition_floor_id':0,#远征的最大关卡id
              'expedition_fail_time':'',#远征失败记录
              'expedition_today_record':[],#远征当天打过的记录
              'expedition_reset_record':[],#远征扫荡重置的记录
              'expedition_first_record':{},#远征首次通过的人
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
    def tutorial_dun_num(self):
        """战斗的次数（新手引导用）
        """  
        if 'tutorial_dun_num' not in self.dungeon_info:
            self.dungeon_info["tutorial_dun_num"] = 5
            self.put()
        return self.dungeon_info["tutorial_dun_num"]
    
    @property
    def dun_special_num(self):
        """精英战场的战斗次数
        """
        if 'dun_special_num' not in self.dungeon_info:
            self.dungeon_info["dun_special_num"] = 3
            self.put()
        return self.dungeon_info["dun_special_num"]
    
    @property
    def max_special_floor_id(self):
        """精英战斗记录
        """
        if 'max_special_floor_id' not in self.dungeon_info:
            self.dungeon_info["max_special_floor_id"] = 0
            self.put()
        return self.dungeon_info["max_special_floor_id"]
    
    @property
    def max_expedition_floor_id(self):
        """远征的战斗
        """
        if 'max_expedition_floor_id' not in self.dungeon_info:
            self.dungeon_info["max_expedition_floor_id"] = 0
            self.put()
        return self.dungeon_info["max_expedition_floor_id"]

    @property
    def expedition_fail_time(self):
        """远征失败的时间
        """
        if 'expedition_fail_time' not in self.dungeon_info:
            self.dungeon_info["expedition_fail_time"] = ''
            self.put()
        return self.dungeon_info["expedition_fail_time"]

    @property
    def expedition_today_record(self):
        """远征今天打的记录
        """
        if 'expedition_today_record' not in self.dungeon_info:
            self.dungeon_info["expedition_today_record"] = []
            self.put()
        return self.dungeon_info["expedition_today_record"]

    @property
    def expedition_reset_record(self):
        """远征重置扫荡记录
        """  
        if 'expedition_reset_record' not in self.dungeon_info:
            self.dungeon_info["expedition_reset_record"] = []
            self.put()
        if len(self.dungeon_info["expedition_reset_record"]) >= 2:
            self.dungeon_info["expedition_reset_record"].pop(0)
            self.put()
        return self.dungeon_info["expedition_reset_record"]
    
    @property
    def expedition_first_record(self):
        """远征第一次通过人的记录
        """
        if 'expedition_first_record' not in self.dungeon_info:
            self.dungeon_info["expedition_first_record"] = {}
            self.put()
        return self.dungeon_info["expedition_first_record"]
    
    @property
    def dun_special_num(self):
        if 'dun_special_num' not in self.dungeon_info:
            self.dungeon_info["dun_special_num"] = 3
            self.put()
        return self.dungeon_info["dun_special_num"]
    
    @property
    def buy_special_dun_num(self):
        if 'buy_special_dun_num' not in self.dungeon_info:
            self.dungeon_info["buy_special_dun_num"] = 0
            self.put()
        return self.dungeon_info["buy_special_dun_num"]        
        
    def update_dungeon(self,floor_id,is_success,mtype,round_num,monster_num):
        """更新战场信息
        """
        dungeon_date_dict = {1:24,2:46,3:66}
        #本次战斗的时间
        total_date = int(round_num * 0.9)
        if total_date < dungeon_date_dict[monster_num]:
            total_date =  dungeon_date_dict[monster_num]
     
        if int(floor_id)  == int(self.dungeon_info['last']['floor_id']):            
            if is_success:
                #如果是boss，则更新max_floor_id和dun_boss_num
                if mtype == 'boss' and int(floor_id) >= int(self.dungeon_info["max_floor_id"]):
                    self.dungeon_info["max_floor_id"] = int(floor_id) + 1
                    self.dungeon_info["dun_boss_num"] = self.dungeon_info.get("dun_boss_num",3) - 1
                #如果是common，则更新成功率记录和战斗时间记录    
                if mtype == "common":
                    self.dungeon_info['sucess_rate_record'].append(100)
                    self.dungeon_info['dungeon_date_record'].append(total_date)
            else:
                if mtype == "common":
                    self.dungeon_info['sucess_rate_record'].append(0)
                    self.dungeon_info['dungeon_date_record'].append(total_date)
        else:
            self.dungeon_info['sucess_rate_record'] = [70,70,70,70,70]
            self.dungeon_info['dungeon_date_record'] = [dungeon_date_dict[monster_num]+10] * 3
            
        if len(self.dungeon_info['sucess_rate_record']) > 10: 
            self.dungeon_info['sucess_rate_record'].pop(0)
            
        if len(self.dungeon_info['dungeon_date_record']) > 5: 
            self.dungeon_info['dungeon_date_record'].pop(0)
            
        if self.tutorial_dun_num < 5:
            self.dungeon_info["tutorial_dun_num"] += 1
            
        self.dungeon_info['last']['floor_id'] = int(floor_id)
        self.dungeon_info['last']['enter_date'] = int(time.time())
        self.dungeon_info['last']['round_num'] = round_num
        self.put()
    
    @property
    def success_rate(self):
        """胜率,是个整数，用的时候需要除以100
        """
        result = sum(self.dungeon_info['sucess_rate_record'])/len(self.dungeon_info['sucess_rate_record'])
        return result/100.0 
    
    @property
    def average_dungeon_num(self):
        """平均战斗时长(单位s/场)
        """
        if len(self.dungeon_info.get("dungeon_date_record",[])) == 0:
            self.dungeon_info['dungeon_date_record'] = [24 + 10] * 3
            self.put()
        result = sum(self.dungeon_info["dungeon_date_record"])/len(self.dungeon_info["dungeon_date_record"])
        return result
    
    @property
    def average_dungeon_date(self):
        """每个小时的战斗次数（单位 场/小时） 计算公式：3600/平均战斗时长
        """
        result = 3600 / self.average_dungeon_num
        return result
    
    @property
    def equip_drop_rate(self):
        """装备掉率 计算公式：(（最小敌将数+最大敌将数）/ 2) * 掉率  * 胜率
        """
        floor_id = self.dungeon_info["last"]["floor_id"]
        dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"]["common"]
        min_monster = dungeon_config.get("min_monster",1)
        max_monster = dungeon_config.get("max_monster",1)
        drop_rate = dungeon_config["reward"]["equip"].get("drop_rate",0)
        result = ((min_monster + max_monster)/2) * drop_rate * self.success_rate
        return result
    
    @property
    def item_drop_rate(self):
        """装备掉率 计算公式：(（最小敌将数+最大敌将数）/ 2) * 掉率  * 胜率
        """
        floor_id = self.dungeon_info["last"]["floor_id"]
        dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"]["common"]
        min_monster = dungeon_config.get("min_monster",1)
        max_monster = dungeon_config.get("max_monster",1)
        drop_rate = dungeon_config["reward"]["item"].get("drop_rate",0)
        result = ((min_monster + max_monster)/2) * drop_rate * self.success_rate
        return result
    
    @property
    def average_coin(self):
        """
                金币获得(单位 经验/小时)计算公式 ：平均每场战斗获得的金钱 * 1个小时的战斗次数 *胜率
                平均每场战斗获得的金钱 = （战场配置中所有怪掉率的金钱/怪的总数 ）*((最大敌将数 +最小敌将数)/2)
        """   
        floor_id = self.dungeon_info["last"]["floor_id"]
        dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"]["common"] 
        min_monster = dungeon_config.get("min_monster",1)
        max_monster = dungeon_config.get("max_monster",1)
        monster_list = dungeon_config["monster"]
        coin = 0
        for m in monster_list:
            monster_config = game_config.monster_config[m]
            coin += monster_config["drop_coin"]
        result = (coin/len(monster_list)) * ((min_monster + max_monster)/2) *\
            self.average_dungeon_num * self.success_rate
        return int(result)
    
    @property
    def average_exp(self):
        """
                经验获得(单位 经验/小时)计算公式 ：平均每场战斗获得的经验 * 1个小时的战斗次数 *胜率
                平均每场战斗获得的经验 = （战场配置中所有怪掉率的经验/怪的总数 ）*((最大敌将数 +最小敌将数)/2)
        """   
        floor_id = self.dungeon_info["last"]["floor_id"]
        dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"]["common"] 
        min_monster = dungeon_config.get("min_monster",1)
        max_monster = dungeon_config.get("max_monster",1)
        monster_list = dungeon_config["monster"]
        exp = 0
        for m in monster_list:
            monster_config = game_config.monster_config[m]
            exp += monster_config["drop_exp"]
            
        result = (exp/len(monster_list)) * ((min_monster + max_monster)/2) * \
            self.average_dungeon_num * self.success_rate
        return int(result)
        
    def offline_dungeon(self,dtype="offline"):
        """离线战斗信息,离线时间小于1次平均战斗时长返回空，离线时间不能大于24小时
        """
        data = {} 
        now_date = int(time.time())
        if dtype == "fast":
            offline_date = 2 * 3600
        else:
            last_dungeon_date = self.dungeon_info["last"].get("enter_date",now_date)
            offline_date = now_date - last_dungeon_date
  
        #每个回合的时间按照每个怪24s算
        if (offline_date < self.average_dungeon_num) or (self.average_dungeon_num == 0):
            return data
          
        #离线时间不能大于24小时    
        if offline_date > 24*3600:
            offline_date = 24*3600   
        #更新上次战斗时间
        self.dungeon_info['last']['enter_date'] = now_date    
        floor_id = self.dungeon_info["last"].get("floor_id",1)
        #战斗的总次数     
        dungeon_num = int(offline_date / self.average_dungeon_num) 
        success_num = int(dungeon_num * self.success_rate)
        if success_num == 0:
            return data
        
        fail_num = dungeon_num - success_num
        if dtype == "fast":
            #根据vip算出金币经验加成奖励
            vip_lv = self.user_base.property_info.vip_lv
            quickPve_reward = float(game_config.vip_config[vip_lv]["quickPve_reward"])
            total_exp = int(quickPve_reward * offline_date * self.average_exp / 3600 )   
            total_coin = int(quickPve_reward * offline_date * self.average_coin / 3600)
        else:
            total_exp = int(offline_date * self.average_exp / 3600)   
            total_coin = int(offline_date * self.average_coin / 3600)
        user_property_obj = UserProperty.get(self.uid)
        user_property_obj.add_exp(total_exp)
        user_property_obj.add_coin(total_coin)
        data["last_lv"] = user_property_obj.property_info["lv"]
        data["floor_id"] = floor_id
        data["dungeon_num"] = dungeon_num
        data["success_num"] = success_num
        data["fail_num"] = fail_num
        data["total_date"] = offline_date
        data["total_coin"] = total_coin
        data["total_exp"] = total_exp
        
        #加装备
        equip_all = {}        #所有的装备
        equip_sells = {}      #卖掉的装备信息
        #equip_not_receive = {}#未领取 
        #not_receive_num = 0   #未领取的装备数
        equip_in_pack = {}    #放到背包里面的装备信息
        from apps.models.user_equipments import UserEquipments
        user_equipments_obj = UserEquipments.get_instance(self.uid)
        dungeon_config = game_config.dungeon_config[str(floor_id)]["rooms"]["common"]
        equip_reward = dungeon_config["reward"]["equip"]  
        equip_drop_num = int(self.equip_drop_rate * dungeon_num)
        #背包上限
        #system_config = game_config.system_config
        #equipNum_limit = system_config["equipNum_limit"]
        #equipExpand_num = system_config["equipExpand_num"]
        #equipExpand_limit = system_config["equipExpand_limit"]
        #max_num = int(equipNum_limit + equipExpand_num * equipExpand_limit)
        #sell_coin = 0 #卖装备得到的金币
        for _ in range(equip_drop_num):
            #根据权重算出掉落的drop_eid,drop_quality
            drop_quality = utils.get_item_by_random_simple([(k,v) for k,v in equip_reward["drop_quality"].items()])
            drop_eid = utils.random_choice(equip_reward["drop_list"],1)[0] 
            #总的装备个数
            if drop_quality in equip_all:
                equip_all[drop_quality]["num"] += 1
            else:
                equip_all[drop_quality] = {}
                equip_all[drop_quality]["num"] = 1 
                               
            eqdbid,equipment = user_equipments_obj.add_equipment(drop_eid,int(drop_quality))
            if equipment["coin"] > 0:
                #自动卖掉的装备     
                if drop_quality in equip_sells:           
                    equip_sells[drop_quality]["num"] += 1
                else:
                    equip_sells[drop_quality] = {}
                    equip_sells[drop_quality]["num"] = 1
                #sell_coin += equipment["coin"] 
            else:
                equip_in_pack.update({eqdbid:equipment})
                
        #加卖出装备的coin
        #if sell_coin > 0:
        #    user_property_obj.add_coin(sell_coin)  
        data['equip_all'] = equip_all
        data['equip_sells'] = equip_sells 
        data['equip_not_receive'] = {}
        data['equip_in_pack'] = equip_in_pack
        
        #加道具
        data['items'] = {} 
        item_reward = dungeon_config["reward"]["item"]
        item_drop_list = item_reward.get("drop_list",{})
        if item_drop_list:
            from apps.models.user_material import UserMaterial
            user_material_obj = UserMaterial.get_instance(self.uid)
            item_drop_num = int(self.item_drop_rate * dungeon_num)
            for _ in range(item_drop_num):
                weight_id = utils.get_item_by_random_simple([(k,v["weight"]) for k,v in item_drop_list.items()])
                drop_item = item_drop_list[weight_id]["item"]
                drop_num = item_drop_list[weight_id]["num"] 
                user_material_obj = UserMaterial.get_instance(self.uid) 
                material = user_material_obj.add_material(drop_item, drop_num)
                if drop_item in data["items"]:
                    data['items'][drop_item]["num"] += drop_num
                else:
                    data['items'].update(material)
        self.put()
        return data