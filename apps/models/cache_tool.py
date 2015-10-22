#-*- coding: utf-8 -*-
  
from apps.oclib.model import BaseModel

class CacheTool(BaseModel):
    """游戏中提供永久存储的key value数据
    """    
    pk = 'cache_key'
    fields = ['cache_key','cache_value'] 
    def __init__(self, cache_key=None):
        """初始化cache   
        """
        self.cache_key = cache_key
        self.cache_value = []
       
    @classmethod
    def get_instance(cls,cache_key):
        obj = super(CacheTool, cls).get(cache_key)
        if not obj:
            obj = cls(cache_key)
            obj.put()
        return obj
    
    def set_value(self,cache_value):
        self.cache_value.append(cache_value)
        self.put()
