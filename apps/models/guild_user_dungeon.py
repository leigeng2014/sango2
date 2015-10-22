# -*- encoding: utf-8 -*- 

from apps.oclib.model import UserModel

class GuildUserDungeon(UserModel):
    #"""个人公会战斗信息
    #"""
    pk = 'uid'
    fields = ['uid','inspire_num','did','damage'] 
    def __init__(self, uid = None):
        self.uid = uid
        self.inspire_num = 0
        self.did = None
        self.damage = 0
        
    @classmethod
    def get(cls, uid):
        obj = super(GuildUserDungeon, cls).get(uid)
        return obj
        
    @classmethod
    def get_instance(cls, uid):
        obj = super(GuildUserDungeon, cls).get(uid)
        if obj is None:
            obj = cls._install(uid)   
        return obj
     
    @classmethod
    def _install(cls, uid):
        obj = cls(uid)
        obj.put()
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base 
    
    def refresh_dungeon_info(self):
        """刷新战斗信息
        """
        self.inspire_num = 0
        self.did = None
        self.damage = 0
        self.put()