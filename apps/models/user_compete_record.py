#-*- coding: utf-8 -*-
import datetime
from apps.oclib.model import HashModel
class UserCompeteRecord(HashModel):
    """用户竞技记录
    """
    pk = 'uid'
    opk = 'ouid'
    fields = ['uid','ouid', 'record_info']

    @classmethod
    def hget(cls,pk,opk):
        obj = super(UserCompeteRecord,cls).hget(pk,opk)
        if obj is None:
            obj = cls.create(pk,opk)
        return obj

    @classmethod
    def create(cls,pk,opk):
        obj = cls()
        obj.uid = pk
        obj.ouid = opk
        obj.record_info = {
        }
        return obj

    def set_record(self, compete_uid,compete_name,ctype,is_success,start_rank='',end_rank='',create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        """记录竞技记录
               参数 :compete_uid 对方uid
            compete_name 对方名字
            ctype 1：挑战，2：被挑战
            start_rank 开始排名
            end_rank   最后的排名
        """
        self.record_info["compete_uid"] = compete_uid
        self.record_info["compete_name"] = compete_name
        self.record_info['type'] = ctype
        self.record_info['is_success'] = is_success
        self.record_info['start_rank'] = start_rank
        self.record_info['end_rank'] = end_rank
        self.record_info['create_time'] = create_time
        self.hput()