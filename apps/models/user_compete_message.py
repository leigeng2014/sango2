#-*- coding: utf-8 -*-
import datetime
from apps.oclib.model import HashModel
class UserCompeteMessage(HashModel):
    """用户竞技留言
    """
    pk = 'uid'
    opk = 'ouid'
    fields = ['uid','ouid', 'record_info']

    @classmethod
    def hget(cls,pk,opk):
        obj = super(UserCompeteMessage,cls).hget(pk,opk)
        if obj is None:
            obj = cls.create(pk,opk)
        return obj

    @classmethod
    def create(cls,pk,opk):
        obj = cls()
        obj.uid = pk
        obj.ouid = opk
        obj.record_info = []
        return obj

    def set_message(self, from_uid,to_uid,content,create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        """留言
               参数 :send_uid:留言的人
            content:留言的内容
        """
        data = {}
        data["from_uid"] = from_uid
        data["to_uid"] = to_uid
        data["content"] = content
        data['create_time'] = create_time
        self.record_info.append(data)
        self.hput()