#-*- coding: utf-8 -*-
import time
import datetime
import json
from django.http import HttpResponse

from apps.common import utils
from apps.common.decorators import needuser
from apps.config import game_config
from apps.common.utils import get_msg

from apps.models.data_log_mod import ChargeRecord
from apps.models.user_property import UserProperty
#from apps.models.user_charge import UserCharge
from apps.models.user_mail import UserMail


def charge_api(oc_user, oid, item_id, platform = '', res_dict={}, request=None, charge_way = '', more_msg={}, charge_money=None):
    """oid:订单号，唯一标示,item_id虚拟产品ID
    """
    data = {'rc': 0}#成功的信息，rc:1为失败
    data['data'] = {'msg': get_msg('charge','success')}

    if ChargeRecord.find({'oid':oid}):
        data["rc"] = 1
        data['data'] = {'msg': get_msg('charge','repeated_order')}
        data['result'] = u'fail_订单重复' 
        return data

    user_property_obj = UserProperty.get(oc_user.uid)
    # 直接充diamond的 item
#     items = [
#         'pay_000','pay_010','pay_020','pay_030','pay_040','pay_050'
#     ]
    diamond_before = user_property_obj.property_info["diamond"]
    diamond_after = 0
    charge_conf = game_config.charge_config
    item_info = charge_conf['charge'][item_id]
    charge_sum_money = item_info["cost"] #人民币数
    user_property_obj.property_info["charge_sum"] += charge_sum_money
    if item_id == "pay_000":
        month_plan_end_time = datetime.datetime.strptime(month_plan_end_time,'%Y-%m-%d')
        now_day = str(datetime.datetime.now().date())
        if month_plan_end_time == '' or (month_plan_end_time != '' and now_day > month_plan_end_time):
            end_day = now_day + datetime.timedelta(days=29)
            user_property_obj.property_info["month_plan_end_time"] = str(end_day)
        else:
            end_day = month_plan_end_time + datetime.timedelta(days=29)
            user_property_obj.property_info["month_plan_end_time"] = str(end_day)

        #邮件发奖励
        sid = utils.create_gen_id()
        user_mail = UserMail.hget(oc_user.uid,sid)
        content = u"月卡礼包领取"
        awards = item_info["rewards"]
        user_mail.set_mail(from_uid='system',mtype="award",content = content,awards=awards)
        charge_sum_money = 30
    else:
        diamond = item_info["num"]
        if oc_user.property_info.first_charge:
            diamond = diamond * 3
            user_property_obj.property_info["first_charge"] = False
        diamond_after = user_property_obj.property_info["diamond"]
        user_property_obj.add_diamond(diamond)       
    user_property_obj.put()

    #作记录
    record_data = {
        "oid": oid,
        "platform": oc_user.platform,
        "lv": user_property_obj.property_info['lv'],
        "cost": item_info['cost'],
        "item_id": item_id,
        "item_num": item_info['num'],
        "create_time": utils.datetime_toString(datetime.datetime.now()),
        "diamond_before": diamond_before,
        "diamond_after": diamond_after,
        "charge_way": charge_way,
    }
    if more_msg:
        record_data.update(more_msg)
    ChargeRecord.set_log(**record_data)
    return data


#@signature_auth
#@session_auth

@needuser
def charge_ios(request):
    """充值回调
    """
    oc_user = request.oc_user
    oid = request.REQUEST.get('oid','')
    item_id = request.REQUEST.get('item_id','')
    platform = request.REQUEST.get('platform','')
    data = charge_api(oc_user, oid, item_id, platform=platform, res_dict={}, request=request, more_msg={})
    data['data']['user_info'] = oc_user.wrapper_info()
    data['data']['server_now'] = int(time.time())
    return HttpResponse(
                json.dumps(data, indent=1),
                content_type='application/x-javascript',
            )

# #@signature_auth
# #@session_auth
# @needuser
# def charge_ios(request):
#     """充值回调
#     """
#     oc_user = request.oc_user
#     now_version = request.REQUEST.get('version','')
#     platform = request.REQUEST.get('platform','')
#     review_version = game_config.system_config.get('review_version','')
# 
#     #审核期间用沙箱url
#     sandbox = 0
#     if review_version and now_version == review_version:
#         apple_url = 'https://sandbox.itunes.apple.com/verifyReceipt'
#         sandbox = 1
#     else:
#         apple_url = 'https://buy.itunes.apple.com/verifyReceipt'
#         
#     #解析参数
#     receipt_data = request.REQUEST.get('receipt')
#     #客户端传来的+变空格了
#     receipt_data = receipt_data.replace(" ", "+")
#     #向Apple验证
#     data = {
#         "receipt-data":receipt_data,
#     }
#     
#     try:
#         from apps.oclib.utils import rkcurl
#         code,res = rkcurl.post(apple_url,json.dumps(data))
#     except:
#         data = {
#             'rc':300,
#             'data':{
#                   'msg':get_msg('login','refresh'),
#                   'server_now':int(time.time()),
#             },
#         }
#         return HttpResponse(
#                     json.dumps(data, indent=1),
#                     content_type='application/x-javascript',
#                 )
#     
#     data = {
#         'rc':1,
#         'result':u'fail_验证失败code:%s'%code,
#         'data':{'msg':get_msg('charge','fail')}
#     }
#     oid = ''
#     item_id = ''
#     #验证成功发给用户商品
#     if code == 200:
#         res_dict = json.loads(res)
#         rc = res_dict["status"]
#         data['result'] = u'fail_status:%s'%rc
#         if rc == 0:
#             oid = res_dict["receipt"]["transaction_id"]
#             item_id = res_dict["receipt"]["product_id"]
#             if sandbox==1:
#                 more_msg = {'sandbox':sandbox}
#             else:
#                 more_msg = {}
#             data = charge_api(oc_user, oid, item_id, platform=platform, res_dict=res_dict, request=request, more_msg=more_msg)
#             data['rc'] = 0
#             
#     data['data']['user_info'] = oc_user.wrapper_info()
#     data['data']['server_now'] = int(time.time())
#     return HttpResponse(
#                 json.dumps(data, indent=1),
#                 content_type='application/x-javascript',
#             )
