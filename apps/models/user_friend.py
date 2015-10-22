#-*- coding: utf-8 -*-
import time
from apps.oclib.model import UserModel
from apps.config import game_config

class UserFriend(UserModel):
    """用户好友信息
    """
    pk = 'uid'
    fields = ['uid','friends','requests']
    def __init__(self):
        """初始化用户好友信息
        """
        self.uid = None
        self.friends = {}
        self.requests = {}
        
    @classmethod
    def get_instance(cls,uid):

        obj = super(UserFriend,cls).get(uid)
        if obj is None:
            obj = cls._install(uid)
        return obj

    @classmethod
    def get(cls,uid):
        obj = super(UserFriend,cls).get(uid)
        return obj

    @classmethod
    def _install(cls,uid):
        """为新用户初始安装好友信息
        """
        obj = cls()
        obj.uid = uid
        obj.friends = {}
        obj.requests = {}        
        obj.put()
        return obj 
    
    @property
    def user_base(self):
        if not hasattr(self, '_user_base'):
            from apps.models.user_base import UserBase
            self._user_base = UserBase.get(self.uid)
        return self._user_base
    
    def add_friend(self,fid):
        """添加好友
        """
        self.friends[fid] = int(time.time())
        self.put()

    def del_friend(self,fid):
        """删除好友
        """
        if fid in self.friends:
            self.friends.pop(fid)
            self.put()

    @property
    def friend_num(self):
        """好友个数
        """
        return len(self.friends)

    def add_request(self,fid):
        """添加好友请求
        """
        time_now = int(time.time())
        self.requests[fid] = time_now
        max_request_num = game_config.system_config.get('max_friend_request',30)
        if len(self.requests) > max_request_num:
            self.requests.pop(self.get_request_ids()[-1])
        self.put()

    def del_request(self,fid):
        """删除好友请求
        """
        if fid in self.requests:
            self.requests.pop(fid)
            self.put()
            
    def get_friend_ids(self):
        """获取好友id列表
        """
        return self.friends.keys()

    def get_request_ids(self):
        """获取好友申请列表
        """
        fids = self.requests.keys()
        fids.sort(key=lambda x:self.requests[x],reverse=True)
        return fids

    def is_friend(self,uid):
        return uid in self.friends