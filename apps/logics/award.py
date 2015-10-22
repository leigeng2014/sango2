# encoding: utf-8
import datetime
from apps.config import game_config
from apps.models.user_cards import UserCards
from apps.models.user_award import UserAward
from apps.models.user_property import UserProperty
from apps.models.user_equipments import UserEquipments
from apps.models.user_material import UserMaterial

def show_sign_bonus(oc_user, params):
    '''返回前端当月签到奖励信息
    '''
    now = datetime.datetime.now()
    month = str(now.month)
    awards = game_config.sign_bonus_config['sign_bonus'].get(month)
    if not awards:
        return 0, {}
    data = {}
    data["result"] = {}
    data["result"]["gifts"] = awards
    user_award_obj = UserAward.get(oc_user.uid)
    if month not in  user_award_obj.sign_record: 
        user_award_obj.sign_record = {month:[]}
        user_award_obj.put() 
    data["result"]['total_sign_days'] = len(user_award_obj.sign_record[month])
    data["result"]["last_sign_days"] = ''
    if data["result"]['total_sign_days'] > 0:        
        data["result"]["last_sign_days"] = user_award_obj.sign_record[month][-1]
    return 0, data

def get_sign_bonus(oc_user, params):
    '''领取签到奖励
    @param day:str 代表第几次签到，如果当月已签到3次则day应该是4
    '''
    day = params.get('day','1')
    user_award_obj = UserAward.get(oc_user.uid)
    now = datetime.datetime.now()
    month = str(now.month)
    data = {'award': {}}
    print day,user_award_obj.sign_record[month]
    if int(day) != len(user_award_obj.sign_record[month]) + 1:
        return 1, {'msg':u"该奖励不能领"} 
    
    if str(now.date()) in user_award_obj.sign_record[month]:
        return 2,{"msg":u"该奖励已经领过了"}  
    
    #添加奖励
    conf = game_config.sign_bonus_config
    award = conf['sign_bonus'].get(month, {}).get(day, {})

    data['award'] = __get_award(oc_user, award)
    # 每天只能签到一次，此字段用来后端判断当天是否已签到过，这时sign_record的下一层字段代表日期
    user_award_obj.sign_record[month].append(str(now.date()))
    user_award_obj.put()
    return 0, data

def __get_award(oc_user, award):
    """给奖励
    """
    user_property_obj = UserProperty.get(oc_user.uid)
    user_equipments_obj = UserEquipments.get_instance(oc_user.uid)
    user_material_obj = UserMaterial.get_instance(oc_user.uid)
    result = {}

    if award["type"] == "coin":
        user_property_obj.add_coin(award["num"])
        result["coin"] = award["num"]

    elif award["type"] == "diamond":
        user_property_obj.add_diamond(award["num"])
        result["diamond"] = award["num"]

    elif award["type"] == "smelting":
        user_property_obj.add_smelting(award)
        result["smelting"] = award["num"]

    elif award["type"] == "cp":
        user_property_obj.add_cp(award)
        result["cp"] = award["num"]

    elif award["type"] == "equip":
        if len(award["id"]) == 1:
            eid = award["id"][0]
        else:
            user_cards_obj = UserCards.get(oc_user.uid)
            category = user_cards_obj.category
            eid = award["id"][int(category)-1]
        eqdbid,equipment = user_equipments_obj.add_equipment(eid,int(award["quality"]))
        if result.get("equipments"):
            result["equipments"].update({eqdbid:equipment})
        else:
            result["equipments"] = {eqdbid:equipment}

    elif award["type"] == "item":
        material = user_material_obj.add_material(award["id"],award["num"])
        if result.get("items"):
            result["items"].append(material)
        else:
            result["items"] = [material]
    return result
