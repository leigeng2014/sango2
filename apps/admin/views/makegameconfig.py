#-*- coding: utf-8 -*-
import sys
import xlrd
import traceback
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

game_config_name_list = [
    ('card_config',u'武将设置'),
    ('card_level_config',u'武将等级配置'),
    ('equip_config',u'装备配置'),
    ('skill_config',u'技能配置'),
    ('dungeon_config',u'普通战场配置'),
    ('monster_config',u'普通敌将配置'),
    ('compete_config',u'争霸配置'),
    ('item_config',u'道具配置'),  
    ('vip_config',u'vip特权配置'),
    ('msg_config',u'提示语配置'),
    ('language_config',u'语言包配置'),
]

config_list = [                               
    'card_config',                                   
    'card_level_config',
    'equip_config',
    'skill_config',
    'dungeon_config',   
    'monster_config',
    'compete_config', 
    'user_init_config',                           
    'item_config',  
    'msg_config',                         
    'language_config',
    'vip_config',
]

def makegameconfig(request):
    """自动生成配置
    """
    data = {}
    config_name = request.GET.get('config_name')
    data['config_name'] = config_name
    data['game_config_name_list'] = game_config_name_list
    return render_to_response('admin/makegameconfig.html', data, context_instance = RequestContext(request))

def is_dict(request):
    if request.method == 'POST':
        dict_value = request.POST['dict_value'].encode('utf-8').replace('\r','').strip()
        try:
            data = {}
            data['config_name'] = 'card_config'
            data['game_config_name_list'] = game_config_name_list
            value = eval(dict_value)
            result = print_dict(value, '')
            data['data'] = result
            return render_to_response('admin/makegameconfig.html', data, context_instance = RequestContext(request))
        except:
            traceback.print_exc(file=sys.stderr)
            return HttpResponse(traceback.format_exc())   

def make_single_config(request):
    data = {}
    config_name = request.GET.get('config_name')
    data['config_name'] = config_name
    data['game_config_name_list'] = game_config_name_list
    if not config_name in config_list:
        data['data'] = 'developering...'
    else:
        data['data'] = make_config(request, config_name)
    return render_to_response('admin/makegameconfig.html', data, context_instance = RequestContext(request))

def __make_config(sheet):
    indented = ''
    _config = make_dict(sheet)
    _config_string = "{\n" + print_dict(_config, indented) + "\n}"
    return _config_string

def make_config(request, config_name):
    try:
        data_string = ''
        filename = request.FILES.get('xls', None)
        excel = xlrd.open_workbook(file_contents = filename.read());
        sheet = excel.sheet_by_name(config_name)
        data_string += __make_config(sheet)
        return str(data_string)

    except:
        traceback.print_exc(file=sys.stderr)
        return traceback.format_exc()

def has_cell2(cell2):
    if cell2 == '':
        return False
    else:
        return True

def make_dict(sheet):
    make_dict = {}
    first_columu = sheet.col_values(0)
    #first_row = sheet.row_values(0)
    for j in range(1, len(first_columu)):
        keys = sheet.cell(j,0).value
        values = sheet.cell(j,1).value
        type_cell = sheet.cell(j,2).value
        keys_list = keys.split('>')
        set_key_value(keys_list, values, make_dict, type_cell)
    return make_dict

def print_dict(values, indented):

    dict_string = ''
    indented += '    '
    klist = values.keys()
    klist.sort()
    for keys in klist:
        if isinstance(keys, str):
            walk_values = values[keys]
            if isinstance(walk_values, dict):
                dict_string += indented + "'" + keys + "':{\n"
                dict_string += print_dict(walk_values, indented)
                dict_string += indented + "},\n"
            elif isinstance(walk_values, str):
                dict_string += indented + "'" + keys + "':'" + walk_values + "',\n"
            elif isinstance(walk_values, (int, float)):
                dict_string += indented + "'" + keys + "':" + str(walk_values) + ",\n"
            elif isinstance(walk_values, unicode):
                walk_values = walk_values.encode('utf-8')
                dict_string += indented + "'" + keys + "':unicode('" + walk_values + "','utf-8'),\n"
            elif isinstance(walk_values, list):
                dict_string += indented + "'" + keys + "':" + str(walk_values) + ",\n"
            elif isinstance(walk_values, tuple):
                dict_string += indented + "'" + keys + "':" + str(walk_values) + ",\n"

    return dict_string

def set_key_value(keys_list, values, make_dict, type_value):
    walk_dict = make_dict
    count = 0
    for key in keys_list:
        key = str(key)
        count += 1
        if not key in walk_dict:
            walk_dict[key] = {}
            if count == len(keys_list):
                if type_value == 'bool':
                    if values == 1:
                        walk_dict[key] = True
                    else:
                        walk_dict[key] = False
                elif type_value == 'list':
                    walk_dict[key] = eval(values)
                elif type_value == 'str':
                    if isinstance(values,float):
                        values = int(values)
                    walk_dict[key] = str(values)
                    
                elif type_value == 'float':
                    values = str(values).replace("'", "")
                    walk_dict[key] = float(values)
                elif type_value == 'int':
                    walk_dict[key] = int(values)
                elif type_value == 'unicode':
                    walk_dict[key] = values
                elif type_value == 'tuple':
                    walk_dict[key] = eval(values)
        walk_dict = walk_dict[key]
