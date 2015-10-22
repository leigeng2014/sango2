#-*- coding: utf-8 -*-
from apps.config import game_config

class UserLevel(object):
    #"""用户等级相关信息
    #"""
    def __init__(self, lv = 1,subarea='1'):
        self.lv = lv  # 用户等级
        self.subarea = subarea
        self.max_data_detail = {}

    @classmethod
    def get(cls, lv = 1, subarea='1'):
        obj = cls(lv,subarea=subarea)
        obj.max_data_detail = game_config.user_level_config['user_lv'].get(str(lv),{})
        return obj

    @property
    def exp(self):
        #"""达到该等级所具有的经验值
        #"""
        return self.max_data_detail.get('exp')