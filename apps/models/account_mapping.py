#-*- coding: utf-8 -*-
import time
from apps.oclib.model import BaseModel
from apps.common import sequence

class AccountMapping(BaseModel):
    #"""用户账号映射信息
    #Attributes:
    #    openid: 第三方唯一id（账号） str
    #    pid: 用户openid str
    #    access_token: 第三方token（密码） str
    #    subarea_uids：pid对应的各取信息     dict
    #    created_at: 创建时间 date
    #"""
    pk = 'pid'
    fields = ['pid','openid', 'access_token', 'created_at', 'subarea_uids']
    def __init__(self):
        """初始化用户账号映射信息
        """
        self.pid = None
        self.openid = ''
        self.access_token = ''
        self.created_at = int(time.time())
        self.subarea_uids = {} # 各分区对应的uid
    
    @classmethod
    def get(cls,pid):
        obj = super(AccountMapping,cls).get(pid)
        return obj
    
#     @classmethod
#     def get_uid(cls, pid,subarea):
#         #"""为每一个用户生成对应的应用自身维护的用户ID
#         #"""
#         obj = cls.get(pid)
#         if not obj:
#             obj = cls.create(pid)
#         uid = obj.subarea_uids.get(subarea)
#         if not uid :
#             uid = sequence.generate()
#             obj.subarea_uids[subarea] = uid
#             obj.put()
#         return uid

    @classmethod
    def get_user_id(cls, pid, subarea):
        """为每一个用户生成对应的应用自身维护的用户ID
        Args:
            id: openid
            subarea: 分区号
        Returns:
            uid: 应用自身维护的用户ID
        """
        account_mapping_obj = cls.get(pid)
        
        if not isinstance(account_mapping_obj,cls):
            account_mapping_obj = cls.create(pid)

        uid = account_mapping_obj.subarea_uids.get(subarea) 
        if not uid :
            uid = sequence.generate()
            account_mapping_obj.subarea_uids[subarea] = uid
            account_mapping_obj.put()
        return uid
    
    @classmethod
    def create(cls,pid):
        obj = AccountMapping()
        obj.openid = ''
        obj.access_token = ''
        obj.pid = pid
        obj.created_at = int(time.time())
        obj.subarea_uids = {}
        return obj   
     
    def get_subarea_uid(self, subarea):
        """获取某个区对于的uid
        """
        return self.subarea_uids.get(subarea, '')
    
    def update_info(self,openid,access_token):
        """更新平台的access_token
        """
        if openid != self.openid or access_token != self.access_token:
            self.openid = openid
            self.access_token = access_token
            self.put()