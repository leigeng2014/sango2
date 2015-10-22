#-*- coding: utf-8 -*-
import sys
import os 
import md5
import random
import traceback
import datetime
import string
import time
from django.conf import settings
from django.core.mail import send_mail

from apps.config import game_config

UUID_STR = 'fWv3wFvwSIJ0RuNthkCBeRXnfk5635kufiD5G84MCRcDydAmpD0zxE8QsPjGsAsI'
UPWD_STR = 'JpHot0lcJascWXF5lGP5YNTiKvEEf6RUfrCQI95R7QMIEJQej73CaWMNFgsrm0Ho'

def print_err():
    sys.stderr.write('=='*30+os.linesep)
    sys.stderr.write('err time: '+str(datetime.datetime.now())+os.linesep)
    sys.stderr.write('--'*30+os.linesep)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write('=='*30+os.linesep)
    
def debug_print(content):
    if settings.DEBUG:
        print content
        
def create_gen_id():
    #"""根据时间生成一个id 
    #"""
    gen_id = str(datetime.datetime.now()).replace(' ', '').replace('-','').replace(':', '').replace('.', '')
    gen_id += str(random.randint(0,9))
    return gen_id

def get_uuid():
    #"""生成一个唯一的用户id
    #"""
    return md5.md5(create_gen_id() + UUID_STR).hexdigest()
    
def get_upwd():
    #"""生成一个唯一的用户密码
    #"""
    return md5.md5(create_gen_id() + UPWD_STR).hexdigest()

def send_exception_mail(request):
    #""" 发送异常信息的mail
    #"""
    error_msg = traceback.format_exc()
    msg = '=='*30+'\n'
    msg += 'err time: '+str(datetime.datetime.now())+'\n'
    msg += '--'*30+'\n'
    msg += error_msg +'\n'
    msg += '--'*30+'\n'
    msg += str(request)
    error_path = request.path
    error_ml = __get_admin_mail_list()
    send_mail('[%s]: Django Error (EXTERNAL IP):' % settings.EMAIL_TITLE+error_path, \
               msg, 'sg2_ios_cn@touchgame.net', error_ml, fail_silently=False, \
              auth_user='sg2',auth_password='sg2')
    
def __get_admin_mail_list():
    mail_list = [a[1] for a in settings.ADMINS]
    return mail_list    
    
def get_msg(category_key, msg_key, subarea='1'):
    #"""获取提示信息 
    #"""
    return game_config.msg_config.get(category_key,{}).get(msg_key,'')

def check_openid(openid):
    openid = str(openid)
    if len(openid) != 32:
        return False
    all_chars = list(string.ascii_lowercase + string.digits)
    for o_str in openid:
        if o_str not in all_chars:
            return False
    return True
        
def create_sig(timestamp, subarea = '1'):
    #"""生成服务器端签名
    #"""
    timestamp_str = str(timestamp)
    signature = md5.new(timestamp_str + settings.SIG_SECRET_KEY).hexdigest()[:7]
    gap_length = random.choice(range(10,22))
    server_sig = game_config.system_config.get('server_sig',True)
    if server_sig:
        padding = md5.new(timestamp_str + 'oc_random_key').hexdigest()[:gap_length]
    else:
        padding_old = md5.new(timestamp_str + 'oc_random_key').hexdigest()[:gap_length-1]
        padding_list = list(padding_old)
        replace_index = random.choice(range(gap_length - 1))
        padding_list[replace_index] = '0'
        now_sum = sum(map(lambda x:int(x,16),padding_list))
        add_num_str = str(4 - now_sum % 4)
        padding_list[replace_index] = add_num_str
        padding = ''.join(padding_list)
    return signature + padding

def is_happen(rate, unit=100):
    #"""根据概率判断事件是否发生
    #args:
    #    rate:概率。可以为小数，也可以为整数。为整数时，总和为unit参数
    #    unit:当rate为整数时，表示总和
    #return:
    #    bool,是否发生
    #"""
    happend = False
    if isinstance(rate, int):
        random_value = random.randint(1, unit)
        if rate >= random_value:
            happend = True
    elif isinstance(rate, float):
        random_value = random.random()
        if rate >= random_value:
            happend = True
    return happend

def get_item_by_random(item_list, weight_list = []):
    #""" 根据权重数组中设定的各权重值随机返回item列表中的item
    #    args:
    #        * item_list - item数组
    #        * weight_list - 权重数组
    #        
    #    returns: 随机指定的item
    #"""
    
    if ((item_list is None) or (len(item_list) == 0)):
        return None
     
    if ((weight_list is None) or (len(weight_list) == 0)):
        random_index = random.randint(0, len(item_list)-1)
    else:
        if (len(item_list) != len(weight_list)):
            return None
        else:
            random_index = get_index_by_random(weight_list)
        
    return item_list[random_index]

def get_index_by_random(weight_list):
    #""" 根据权重数组中设定的各权重值随机返回该权重数组的下标
    #    args:
    #        * weight_list - 权重数组
    #        
    #    returns: int 权重数组的下标
    #"""
    
    total_weight = 0
    weight_list_temp = []
    
    #计算总权重
    for weight in weight_list:
        total_weight = total_weight + weight
        weight_list_temp.append(total_weight)

    #在总权重数中产生随机数
    random_value = random.randint(1, total_weight)
    
    #根据产生的随机数判断权重数组的下标
    list_index = 0
    for weight_temp in weight_list_temp:
        if random_value <= weight_temp:
            break
        list_index = list_index + 1
        
    return list_index

def get_item_by_random_simple(item_weight_list):
    #""" 根据权重数组中设定的各权重值随机返回item列表中的item
    #    args:
    #        * item_weight_list - item,权重数组
    #        
    #    returns: 随机指定的item
    #"""
    if ((item_weight_list is None) or (len(item_weight_list) == 0)):
        return None
    
    item_list = []
    weight_list = []
    
    for item_weight in item_weight_list:
        item_list.append(item_weight[0])
        weight_list.append(item_weight[1])
        
    return get_item_by_random(item_list, weight_list)

def random_choice(alist, num):
    #""" 随机从列表中选择指定数量的元素
    #"""
    if num <= 0:
        return []
    list_len = len(alist)
    key_len = list_len if list_len < num else num
    return random.sample(alist, key_len)

def datetime_toString(dt,strformat='%Y-%m-%d %H:%M:%S'):
    #"""把datetime转成字符串
    #"""
    return dt.strftime(strformat)

#把字符串转成datetime
def string_toDatetime(string,strformat='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(string, strformat)

#把字符串转成时间戳形式
def string_toTimestamp(strTime):
    return int(time.mktime(string_toDatetime(strTime).timetuple()))

#把时间戳转成字符串形式
def timestamp_toString(stamp,strformat='%Y-%m-%d %H:%M:%S'):
    return time.strftime(strformat, time.localtime(stamp))

#把datetime类型转外时间戳形式
def datetime_toTimestamp(dateTim):
    return int(time.mktime(dateTim.timetuple()))

#把datetime类型转外时间戳形式
def timestamp_toDatetime(stamp,strformat='%Y-%m-%d %H:%M:%S'):
    strTime = timestamp_toString(stamp,strformat)
    return string_toDatetime(strTime,strformat)

def is_sense_word(words, subarea = '1'):
    #"""检查是否是敏感词
    #"""
    sensitive_words = game_config.maskword_config.get('sensitive_words',[])
    _name = words.lower()
    special_words = ['%','$','#','@','&','*','^','~','`','|']
    for w in special_words:
        if w in _name:
            return True    
    for sense_word in sensitive_words:
        if _name.find(sense_word) >= 0:
            return True
    return False

def check_name(uid,name):
    """检查用户名
    """
    from apps.models.user_name import UserName
    if UserName.get(name):
        return False
    try:
        UserName.set_name(uid, name)
    except:
        return False
    return True