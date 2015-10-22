#-*- coding: utf-8 -*-
import time

from apps.models.config import Config

reload_time = int(time.time())

all_config_name_list = [
    ('system_config',u'系统配置'),
    ('card_config',u'角色配置'),
    ('card_category_config',u'角色类型配置'),
    ('card_level_config',u'角色等级配置'),
    ('card_init_config',u'角色初始配置'),
    
    ('skill_config',u'角色技能配置'),
    ('dungeon_config',u'战场配置'),
    ('special_dungeon_config',u'精英战场配置'),
    ('expedition_dungeon_config',u'远征战场配置'),
    ('monster_config',u'敌将配置'),
    ('equipment_config',u'装备配置'),
    #('second_equipment_config',u'装备副属性配置'),
    ('vice_attr_config',u'装备副属性配置'),
    ('special_attr_config',u'神器属性配置'),
    ('special_attr_level_config',u'神器属性等级配置'),
    ('equipment_strengthen_config',u'装备强化配置'),
    ('equipment_smelting_config', u'装备熔炼配置'),
    ('equipment_forge_config',u'装备打造&洗练配置'),
    ('equipment_drop_config',u'装备掉落配置'),    
    ('equipment_lv_config',u'装备等级配置'),  
     #公会配置    
    ('guild_config',u'公会相关配置'),
    ('material_config',u'道具配置'),
    ('gem_config', u'宝石配置'),
    ('team_develop_config',u'佣兵培养配置'),
    ('team_config',u'佣兵配置'), 
    ('compete_config',u'竞技配置'),
    ('compete_npc_config',u'竞技npc配置'),
    
    ('shop_config',u'商品配置'),
    ('shop_extra_config',u'商店设定配置'),
    ('cp_shop_config',u'荣誉商店配置'),
    
    ('award_config',u'礼包配置'),
    ('mail_config',u'系统邮件配置'),
    ('sign_bonus_config',u'每日签到配置'),
    ('charge_config',u'充值配置'),
    ('vip_config',u'VIP配置'),
    ('title_config',u'称号配置'),
    
    ('language_config',u'语言包配置'),
    ('msg_config',u'提示语配置'),
    ('maskword_config',u'屏蔽字配置'),
]

#根据属性列表，加载游戏配置信息
for config_name in all_config_name_list:
    config = Config.get(config_name[0])
    if config is None:
        config = Config.create(config_name[0])
        config.put()
    try:
        exec(config_name[0] + '=eval(config.data)')
    except Exception,e:
        print 'settings loading error:',config_name[0]
        print 'message:',e.message
        print config.data
        exec(config_name[0] + '={}')
