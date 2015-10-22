#-*- coding: utf-8 -*-
from apps.models.virtual.soldier import Soldier 

class Dungeon(object):
    """战斗"""
    def __init__(self, uid):
        """初始化战场数据
        """
        self.uid = uid
        self.first_army = []
        self.second_army = []        
        self.result = []  
        self.is_success = 0

    def load_first_army(self,first_army):
        """加载第一军队"""
        for i,card in enumerate(first_army):
            solider = Soldier(self,card)
            solider.position = '1_'+ str(i)
            self.first_army.append(solider)
 
    def load_second_army(self,second_army):
        """加载第二军队 """
        for i,card in enumerate(second_army):
            solider = Soldier(self,card)
            solider.position = '2_'+str(i)
            self.second_army.append(solider)     
               
    def is_dungeon_finish(self):
        """判断战斗是否结束
        """   
        #第二军队全死掉了
        if not [soldier for soldier in self.second_army if soldier.hp > 0]:
            self.is_success = 1
            return 1   
                     
        #第一军队全死掉了
        if not [soldier for soldier in self.first_army if soldier.hp > 0]:
            return 2        
        return 0 

    def run(self):
        """开始战斗
        """   
        max_round = 50 #最大回合数
        while max_round > 0:
            max_round -= 1  
            if self.is_dungeon_finish() > 0:
                break   
            first_army_len = len(self.first_army)
            second_army_len = len(self.second_army)
            for i in range(max(first_army_len,second_army_len)):
                if first_army_len > i:
                    self.first_army[i].action()                    
                if second_army_len > i:
                    self.second_army[i].action()