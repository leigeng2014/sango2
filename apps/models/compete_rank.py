#-*- coding: utf-8 -*-
from apps.oclib.model import TopModel

RANK = {}        
class CompeteRank(TopModel):
    #"""竞技排行榜排名信息
    #"""
    def __init__(self, subarea):
        #"""初始化
        #"""
        self.subarea = subarea
        self.top_name = 'CompeteRank_' + self.subarea 
       
    def set(self, name, score):
        #"""设置排行榜
        #"""       
        obj = super(CompeteRank, self).set(name, score)
        return obj

def get_compete_rank(subarea):
    #"""统一管理pvp的排行榜
    #"""
    if not subarea in RANK:
        RANK[subarea] = CompeteRank(subarea)
    return RANK[subarea]

class Rank(TopModel):
    #"""排行榜
    #"""
    def __init__(self,subarea,name):
        #"""初始化
        #"""
        self.subarea = subarea
        self.top_name = name + self.subarea 
      
    def set(self, name, score):
        #"""设置排行榜
        #"""       
        obj = super(Rank, self).set(name, score)
        return obj