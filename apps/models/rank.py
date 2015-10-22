#-*- coding: utf-8 -*-
from apps.oclib.model import TopModel
from apps.config import game_config

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
    

def update_force_rank(uid):
    """更新战力排行榜
    """
    from apps.models.user_base import UserBase
    from apps.models.user_cards import UserCards    
    user_base_obj = UserBase.get(uid)
    user_cards_obj = UserCards.get(uid)
    force_rank_obj = Rank(user_base_obj.subarea,'force_rank')                          
    force_rank_obj.set(uid,user_cards_obj.force)
    cid = user_cards_obj.cid
    category = game_config.card_config[cid]["category"]
    card_rank_obj = Rank(user_base_obj.subarea,'ca' + category + '_rank')
    card_rank_obj.set(uid,user_cards_obj.force)