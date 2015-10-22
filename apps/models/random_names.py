#-*- coding: utf-8 -*-
from apps.oclib.model import MongoModel

class Random_Names(MongoModel):
    """随机名字
    """
    pk = 'name'
    fields = ['name','random']
    def __init__(self):
        pass


