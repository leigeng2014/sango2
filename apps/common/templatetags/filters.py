#-*- coding: utf-8 -*-
import time

from django import template
register = template.Library()

def star(para):
    para = int(para)
    return '★' * para

#把时间戳转成字符串形式
def timestamp_toString(stamp):
    if stamp:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stamp))
    else:
        return ''

def get_equip_category(eid):
    from apps.config import game_config
    return game_config.equipment_config[eid]["category"]   

def get_equip_type(eid):
    from apps.config import game_config
    return game_config.equipment_config[eid]["type"]

def get_equip_name(eid):
    from apps.config import game_config
    return game_config.language_config.get(eid+"_Name")

def get_item_name(eid):
    from apps.config import game_config
    return game_config.language_config.get(eid+"_Name")

register.filter('star', star)
register.filter('timestamp_toString', timestamp_toString)
register.filter('get_equip_category', get_equip_category)
register.filter('get_equip_type', get_equip_type)
register.filter('get_item_name', get_item_name)
register.filter('get_equip_name', get_equip_name)