#-*- coding: utf-8 -*-
import md5
import datetime
import apps.admin.auth

from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.admin.models import Moderator
from apps.models.config import Config
from apps.admin.decorators import require_permission
from apps.admin.views.forms import  ModeratorCreationForm,ModeratorManageForm,ModeratorResetPasswordForm
from apps.admin import admin_configuration
from apps.config import update as config_update
from apps.config import config_update_version
from apps.config.game_config import all_config_name_list


def index(request):
    moderator = apps.admin.auth.get_moderator_by_request(request)
    if moderator is None:
        return HttpResponseRedirect("/admin/login/")
    else:
        return HttpResponseRedirect("/admin/main/")


@require_permission
def main(request):
    return render_to_response("admin/main.html",{"appname":settings.APP_NAME},RequestContext(request))

def login(request):
    """
        首页，登录用
    """
    appname = settings.APP_NAME
    if request.method == "POST":
        username = request.POST.get("username")
        password = md5.md5(request.POST.get("password")).hexdigest()
        if not username or not password:
            return render_to_response("admin/login.html",{'status':1,"appname":appname},RequestContext(request))
        mid = apps.admin.auth.get_mid_by_username(username)
        if mid is None:
            return render_to_response("admin/login.html",{"status":2,"appname":appname},RequestContext(request))
        moderator = apps.admin.auth.get_moderator(mid)
        if moderator is None:
            return render_to_response("admin/login.html",{"status":2,"appname":appname},RequestContext(request))
        if not moderator.is_staff:
            return render_to_response("admin/login.html",{"status":4,"appname":appname},RequestContext(request))
        if moderator.check_password(password):
            response = HttpResponseRedirect("/admin/main/")
            apps.admin.auth.login(request,response,moderator)
            return response
        else:
            return render_to_response("admin/login.html",{"status":3,"appname":appname},RequestContext(request))
    else:
        return render_to_response("admin/login.html",{"appname":appname},RequestContext(request))

def registration(request):
    """
    注册帐号
    """
    username = request.POST.get("username")
    password = request.POST.get("password")
    if not username or not password:
        return render_to_response("admin/registration.html",{"appname":'a'},RequestContext(request))
    else:
        moderator = Moderator.get(username)
        if moderator:
            return HttpResponse("该用户名已经存在，可以员工编号做为后缀")
        else:
            moderator = Moderator.get_instance(username)
            moderator.username = username
            moderator.is_staff = 0
            moderator.set_password(md5.md5(password).hexdigest())
            moderator.in_review = True
            moderator.put()
            msg = "username: " + username + '\n'
            msg += str(request)
            error_ml = ['haiou.chen@newsnsgame.com']
            send_mail('[%s]: registration: ' % (request.path), msg, 'maxstrike_ios_cn@touchgame.net', error_ml, fail_silently=False,\
            auth_user='maxstrike_ios_cn',auth_password='oneclick101')

        return HttpResponse("请耐心等待审核通过")

def logout(request):
    """
    登出
    """
    response = HttpResponseRedirect("/admin/")
    apps.admin.auth.logout(request,response)
    return response

@require_permission
def left(request):
    """
    左侧列表页
    """
    #获取当前用户
    moderator = apps.admin.auth.get_moderator_by_request(request)
    index_list = admin_configuration.view_perm_mappings.get_allow_index_paths(moderator)
    message = False
    if moderator.permissions == 'super':
        in_review_list = Moderator.find({'in_review' : True}) 
        if in_review_list:
            message = True
    return render_to_response("admin/left.html",{"index_list":index_list, 'message': message},RequestContext(request))

@require_permission
def moderator_list(request):
    """
    管理员列表
    """
    # 取数据库
    from apps.admin.models import Moderator
    mod_list = Moderator.find({'is_staff':1})
    return render_to_response("admin/moderator_list.html",{"moderator_list":mod_list},RequestContext(request))

def agree_inreview(request):
    """
    带审核的帐号列表列表
    """
    # 取数据库
    from apps.admin.models import Moderator
    mod_list = Moderator.find({'in_review':True})
    return render_to_response("admin/moderator_list.html",{"moderator_list":mod_list},RequestContext(request))

@require_permission
def moderator_permissions(request):
    mid = request.GET.get("mid")
    if mid is None:
        return
    moderator = apps.admin.auth.get_moderator(mid)

    perms = []
    for perm in moderator.get_permissions():
        perms.append(admin_configuration.all_permissions[perm])

    return render_to_response("admin/moderator_permissions.html",{"perm_list":perms},RequestContext(request))

@require_permission
def add_moderator(request):
    """
     新建管理员
    """
    if request.method == "POST":
        from apps.admin.models import Moderator
        form = ModeratorCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            permissions = form.cleaned_data["permissions"]
            moderator = Moderator.get_instance(username)
            moderator.username = username
            moderator.is_staff = 1
            moderator.email = form.cleaned_data["email"]
            moderator.last_login = datetime.datetime.now()
            moderator.set_password(md5.md5(password).hexdigest())
            moderator.set_permissions(permissions)
            moderator.put()
            return HttpResponseRedirect('/admin/moderator/add_moderator_done/')
    else:
        form = ModeratorCreationForm()

    return render_to_response("admin/add_moderator.html",{'form':form},context_instance = RequestContext(request))

def add_moderator_done(request):
    return render_to_response("admin/add_moderator_done.html")

@require_permission
def manage_moderator(request):
    """
        管理员管理表单
    """
    mid = request.GET.get("mid")
    if mid is None:
        return render_to_response("admin/manage_moderator.html",{"status":1,"mid":mid},RequestContext(request))
    moderator = apps.admin.auth.get_moderator(mid)
    if moderator is None:
        return render_to_response("admin/manage_moderator.html",{"status":2,"mid":mid},RequestContext(request))
    if request.method == "POST":
        form = ModeratorManageForm(data = request.POST)
        if form.is_valid():
            password = md5.md5(form.cleaned_data["password1"]).hexdigest()
            permissions = form.cleaned_data["permissions"]
            moderator.is_staff = 1
            #密码
            if form.cleaned_data["password1"]:
                if password != "d41d8cd98f00b204e9800998ecf8427e":
                    moderator.set_password(password)
            #权限
            moderator.in_review = False
            moderator.clear_permissions()
            moderator.set_permissions(permissions)

            return HttpResponseRedirect("/admin/moderator/manage_moderator_done/")
        else:
            return render_to_response("admin/manage_moderator.html",{"form":form,"mid":mid},RequestContext(request))

    form = ModeratorManageForm({"permissions":moderator.get_permissions()})
    return render_to_response("admin/manage_moderator.html",{'moderator':moderator,'form':form,"mid":mid},RequestContext(request))

@require_permission
def manage_moderator_done(request):
    return render_to_response("admin/manage_moderator_done.html",{},RequestContext(request))

@require_permission
def change_password(request):
    """
        修改密码
    """
    moderator = apps.admin.auth.get_moderator_by_request(request)
    if request.method == "POST":
        form = ModeratorResetPasswordForm(request.POST)
        if form.is_valid():
            moderator.set_password(md5.md5(form.cleaned_data["password1"]).hexdigest())
            moderator.put()
            return render_to_response("admin/change_password_done.html",{},RequestContext(request))
    else:
        form = ModeratorResetPasswordForm()
    return render_to_response("admin/change_password.html",{'moderator':moderator,'form':form},RequestContext(request))

@require_permission
def delete_moderator(request):
    """
       删除管理员
    """
    if request.method == "POST":
        mid = request.GET.get("mid")
        if mid is None:
            return render_to_response("admin/delete_moderator.html",{'status':1},RequestContext(request))
        moderator = apps.admin.auth.get_moderator(mid)
        if moderator is None:
            return render_to_response("admin/delete_moderator.html",{'status':2},RequestContext(request))

        apps.admin.auth.delete_moderator(mid,moderator.mid)
        return HttpResponseRedirect("/admin/moderator/delete_moderator_done/")
    else:
        return render_to_response("admin/delete_moderator.html",{},RequestContext(request))

def delete_moderator_done(request):
    """
    删除管理员成功
    """
    return render_to_response("admin/delete_moderator_done.html",{},RequestContext(request))

@require_permission
def game_setting(request):
    """游戏配置
    """
    config_name = request.GET.get('config_name')
    saved = False
    subareas_conf = Config.get('subareas_conf')
    
    if not subareas_conf:
        subareas_conf = Config.create(config_name)
    subareas_conf_dict = eval(subareas_conf.data)
    return_subareas_conf = []
    for key in sorted(subareas_conf_dict.keys()):
        return_subareas_conf.append((key, subareas_conf_dict[key]))
    if config_name:
        #修改具体的一个
        config = Config.get(config_name)
        if not config:
            config = Config.create(config_name)
        config_value = config.data
        if request.method == 'POST':
            config_value = request.POST['config_value'].encode('utf-8').replace('\r','').strip()
            config.data = config_value            
            try:
                eval(config_value)
            except Exception,e:
                return HttpResponse('<script>alert("填写错误%s，请检查");history.go(-1)</script>' % str(e))        
            config.put()
            config_update()
            saved = True
    else:
        #显示所有
        config_value = None

    config_name = request.GET.get('config_name')
    data = {}
    data['subareas_conf'] = return_subareas_conf
    if not config_name or config_name == 'subareas_conf':
        data['config_title'] = u'分区设置' 
    else:
        data['config_title'] = filter(lambda x:x[0] == config_name,all_config_name_list)[0][1] if config_name else ''

    data['game_config_name_list'] = all_config_name_list
    data['config_name'] = config_name
    data['config_title'] += '__%s' % config_name
    data['config_value'] = config_value
    data['saved'] = saved

    return render_to_response('admin/game_setting.html',data,context_instance = RequestContext(request))

