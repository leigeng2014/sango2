#-*- coding: utf-8 -*-
import os
BASE_ROOT = os.path.dirname(os.path.dirname(__file__))

DEBUG = True

TEMPLATE_DEBUG = DEBUG

LOCAL_DEBUG = False

ENVIRONMENT_TYPE = 'stg'

BASE_URL = ''

ADMINS = (
)

EMAIL_HOST = 'mail.touchgame.net'

EMAIL_PORT = 25

EMAIL_USE_TLS=False

TIME_ZONE = 'Asia/Shanghai'

LANGUAGE_CODE = 'ja'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_ROOT = BASE_ROOT + '/static/images'

MEDIA_URL = BASE_URL + '/images/'

STATIC_ROOT = BASE_ROOT + '/static/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'apps.common.middlewares.simple.P3PMiddleware',
    'apps.common.middlewares.exception.ExceptionMiddleware',
    'apps.common.middlewares.storage.StorageMiddleware',
)

ROOT_URLCONF = 'apps.urls'

TEMPLATE_DIRS = (
    BASE_ROOT + '/apps/templates',
)

INSTALLED_APPS = (
    'apps.admin',
    'apps.common',
)

AUTH_AGE = 12

SECRET_KEY = 'bdm@ktf0p7ee_sa7^mvg%i-d=b66jpd4qqomhb%upzg^s*05#v'

SIG_SECRET_KEY = 'e#!(MO4gfu!^392)_()rm3'

CACHE_PRE = "plage_"

PIER_USE = True

#appid和平台id
OC_APP_ID = ''# 病毒

OC_PLATFORM_ID = '1'#平台id

#storage config
STORAGE_INDEX = '1'

STORAGE_CONFIG = {
    '1':{
        'redis':[{'host':'10.200.55.32','port':6398,'db':'0'}],  #一组redis 用来存储游戏数据
        'mongodb':{'host':'10.200.55.32','port':27017,'db':'plague','username':'plagueu','password':'W3aMi6W7Q15iUN6wcHfShC5f8'}, #一个mongodb 用来存储游戏数据
        'top_redis':{'host':'10.200.55.32','port':6398,'db':'1'},  #一个redis 用来做排行榜
        'log_mongodb':{'host':'10.200.55.32','port':27017,'db':'logplague','username':'logplagueu','password':'Usex7ut6i3613ABRB95c4AEiU'},#一个mongodb 用来日志数据存储
        'secondary_log_mongodb':{'host':'10.200.55.32','port':27017,'db':'logplague','username':'logplagueu','password':'Usex7ut6i3613ABRB95c4AEiU'},
    },
}

#AES KEY
AES_KEY = "e^qhim=ve^dw+gsz1^&5e(x#@uamq*-&"
APP_NAME = '病毒测试服务器'
EMAIL_TITLE = 'plague-cn'