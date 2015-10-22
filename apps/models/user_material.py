#-*- coding: utf-8 -*-
import copy
import random
from apps.common import utils

from apps.config import game_config
from apps.oclib.model import UserModel
from apps.models.user_property import UserProperty

class UserMaterial(UserModel):
    """用户材料信息
    """
    pk = 'uid'
    fields = ['uid', 'materials']

    def __init__(self, uid=None):
        self.uid = uid
        self.materials = {
        }
        
    @classmethod
    def get_instance(cls, uid):
        obj = super(UserMaterial, cls).get(uid)
        if not obj:
            obj = cls.create(uid)    
            obj.put()        
        return obj    
    
    @classmethod
    def get(cls, uid):
        obj = super(UserMaterial, cls).get(uid)
        return obj
    
    @classmethod
    def create(cls, uid):
        obj = cls()
        obj.uid = uid 
        return obj
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base

    def add_material(self, mid, num=1):
        """添加道具
        """
        if mid not in self.materials:
            material = {}
            material["num"] = num

            material_config = game_config.material_config
            if not mid in material_config:
                return False
            
            mtype = material_config[mid]['type']
            #根据mid读取材料类型
            material['type'] = mtype
            if mtype == '1':
                material['exp'] = 0
            self.materials[mid] = material
        else:
            material = self.materials[mid]
            material["num"] = material["num"] + num
        self.put()
        #返回添加的个数
        copy_material = copy.deepcopy(material)
        copy_material["num"] = num
        return {mid: copy_material}    

    def minus_material(self, mid, num):
        """减少道具
        """
        if mid not in self.materials:
            return False
        material = self.materials[mid]
        db_num = material["num"]
        if db_num < num:
            return False
        db_num -= num
        if db_num == 0:
            self.materials.pop(mid)
        else:
            material["num"] = db_num
        if "exp" in material:
            material["exp"] = 0
        self.put()
        return True
    
    def has_material(self,mid):
        """判断材料是否存在
        """
        result = 0
        if mid in self.materials:
            result = self.materials[mid]["num"]
        return result
