#-*- coding: utf-8 -*-
from apps.oclib.model import UserModel
from apps.config import game_config

class UserTitle(UserModel):
    """用户称号信息
    """
    pk = 'uid'
    fields = ['uid','title_info']
    
    def __init__(self,uid = None):
        self.uid = uid  
        self.title_info = {
                           'is_used':'',
                           'title_record':[],
                           } 

    @classmethod
    def get(cls,uid):
        obj = super(UserTitle,cls).get(uid)
        return obj
    
    @classmethod
    def get_instance(cls,uid):
        obj = super(UserTitle,cls).get(uid)
        if obj is None:
            obj = cls._install(uid)
            return obj
        return obj
    
    @classmethod
    def _install(cls,uid):
        obj = cls(uid)
        obj.put()        
        return obj 

    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    def set_title(self,title_type):
        """添加称号
        """
        title_config = game_config.title_config
        for k,v in title_config.items():
            if title_type == v["type"]: 
                if k not in self.title_info["title_record"]:
                    is_pass = False
                    #通过燃烧塔
                    if title_type == '1':
                        from apps.models.user_dungeon import UserDungeon
                        user_dungeon_obj = UserDungeon.get_instance(self.uid)
                        max_expedition_floor_id = user_dungeon_obj.max_expedition_floor_id
                        if v["level"] == 'hard' and max_expedition_floor_id > 13:
                            is_pass = True
                        if v["level"] == 'special' and max_expedition_floor_id > 26:
                            is_pass = True                            
                    #竞技第一名        
                    elif title_type == '2':
                        from apps.models.compete_rank import get_compete_rank
                        compete_rank_obj = get_compete_rank(self.user_base.subarea)
                        my_rank = compete_rank_obj.score(self.uid)
                        if int(my_rank) == 1:
                                is_pass = True
                    #全身都是神器
                    elif title_type == '3':
                        from apps.models.user_equipments import UserEquipments
                        from apps.models.user_cards import UserCards
                        user_equipments_obj = UserEquipments.get_instance(self.uid)
                        equipments = user_equipments_obj.equipments
                        user_cards_obj = UserCards.get(self.uid)
                        flag = True
                        for _,_v in user_cards_obj.equipments.items():
                            if (not _v) or (_v not in equipments):
                                flag = False
                                continue 
                            if len(equipments[_v]["special_attr"]) > 0:
                                flag = False                                
                        if flag is True:
                            is_pass = True                    
                    #竞技强者
                    elif title_type == '4':
                        from apps.models.compete_rank import get_compete_rank
                        compete_rank_obj = get_compete_rank(self.user_base.subarea)
                        my_rank = compete_rank_obj.score(self.uid)
                        if int(my_rank) <= 20:
                            is_pass = True
 
                    if is_pass is True:         
                        self.title_info["title_record"].append(k)
                        self.put()
        return True 
    
    def use_title(self,tid):
        """使用称号
        """
        if tid == '':
            self.title_info["is_used"] = ''
        else:
            if tid not in self.title_info["title_record"]:
                return False
            self.title_info["is_used"] = tid
        self.put()
        return True