#-*- coding: utf-8 -*-
from apps.oclib.model import BaseModel

MAX_USER_NUM = 2000
class LevelUser(BaseModel):
    """根据ip选择用户
    """
    pk = 'subarea'
    fields = ['subarea','users']
    
    def __init__(self, subarea = 1):
        self.subarea = subarea
        self.users = []

    @classmethod
    def get_instance(cls,subarea):
        obj = super(LevelUser,cls).get(subarea)
        if obj is None:
            obj = cls._install(subarea)
        return obj
    
    @classmethod
    def _install(cls,subarea):
        obj = cls(subarea)
        obj.put()
        return obj
    
    def add_user(self,uid):
        """添加用户
        """ 
        if uid not in self.users:
            self.users.insert(0,uid)
            self.users = self.users[0:MAX_USER_NUM]             
            self.put() 