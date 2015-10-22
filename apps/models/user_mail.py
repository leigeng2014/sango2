#-*- coding: utf-8 -*-
import datetime
from apps.oclib.model import HashModel

class UserMail(HashModel):
    """用户游戏邮件基本信息
    """
    pk = 'uid'
    opk = 'ouid'
    fields = ['uid','ouid', 'mail_info']

    @classmethod
    def hget(cls,pk,opk):
        obj = super(UserMail,cls).hget(pk,opk)
        if obj is None:
            obj = cls.create(pk,opk)
        return obj

    @classmethod
    def create(cls,pk,opk):
        obj = cls()
        obj.uid = pk
        obj.ouid = opk
        obj.mail_info = {
        }
        return obj

    def set_mail(self,from_uid='system',mtype="common",content='',awards={},create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        """发邮件
        @params from_uid:str 发邮件的人uid 如果是系统邮件为system 
        @params mtype:str 邮件的类型 common：普通邮件，award：有奖励的邮件，compete:竞技失败邮件，chat聊天邮件
        @params content:str 邮件的内容
        @params awards:dict 奖励的内容
        @params create_time:创建时间 
        """
        self.mail_info['from_uid'] = from_uid
        self.mail_info['type'] = mtype
        self.mail_info['content'] = content
        self.mail_info['awards'] = awards
        self.mail_info['create_time'] = create_time
        self.hput()
                                                                                                                                                                  
    @classmethod
    def hgetall(cls,pk):
        all_data = super(UserMail,cls).hgetall(pk)
        if all_data is None:
            all_data = {}
        return all_data