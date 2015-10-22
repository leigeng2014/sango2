#-*- coding: utf-8 -*-
import time

from django.conf import settings

from apps.models import redis_tool
from apps.models.redis_tool import RedisTool
from apps.config import game_config

def update():
    RedisTool.set(settings.CACHE_PRE+'config_update_time', time.time(), 72*60*60)   
    
def config_update_version(subarea, config_name):
    redis_tool.set_config_version(subarea, config_name)  
    redis_tool.RedisTool.set(settings.CACHE_PRE+'system_config_update_time', time.time(), 72*60*60)
    
def reload_all():
    from apps.common import utils
    try:        
        reload_time = redis_tool.RedisTool.get(settings.CACHE_PRE+'config_update_time')
        if (not reload_time) or (reload_time and game_config.reload_time < reload_time):            
            reload(game_config)
            print 'game_config reloaded......'
    except:        
        utils.print_err()