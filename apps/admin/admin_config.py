#-* coding:utf-8 -*-
# 权限列表
permissions = [
    {
        "code":"super",
        "description":u"超级管理权限,能干全部事情"
    },
    {
        "code":"submit_setting",
        "description":u"允许修改配置"
    },
]

# view method mapping permissions
# mappings：view函数映射关系
#   path: view path
#   index:  是否是管理后台的导航页面
#   permissions: 额外指定的权限列表
views_perms_mappings={
    "index":[
        {
            "path":'/admin/moderator/moderator_list/',
            "name":"管理员管理",
            "order":0,
            "permissions":"super",
        },
        {
            "path":'/admin/moderator/agree_inreview/',
            "name":"待审核列表",
            "order":0,
            "permissions":"super",
        },
        {
            "path":'/admin/change_password/',
            "name":"修改密码",
            "order":0,
            "permissions":"all",
        },
        {
            "path": '/admin/game_setting/',
            "name": '游戏设置',
            "order": 0,
            "permissions": "submit_setting",
        },
        {
            "path": '/admin/user/?user_type=view',
            "name": '查看用户',
            "order": 0,
            "permissions": "all",
        },
        {
            "path": '/admin/user/',
            "name": '修改用户',
            "order": 0,
            "permissions": "all",
        }, 
        {
            "path": '/admin/tool/',
            "name": '运营工具',
            "order": 0,
            "permissions": "all",
        },              
        {
            "path": '/admin/makegameconfig/',
            "name": '生成配置',
            "order": 0,
            "permissions": "all",
        },    
        {
            "path":'/admin/logout/',
            "name":"登出",
            "order":0,
            "permissions":"all",
        },

    ],
    "mappings":[
        {
            "path" : r'^/admin/main/$',
            "permissions" : "all"
        },
        {
            "path" : r'^/admin/left/$',
            "permissions" : "all"
        },
        {
            "path" : r'/admin/moderator/moderator_list/',
            "permissions" : "super"
        },
        {
            "path" : r'/admin/moderator/view_permissions/',
            "permissions" : "super"
        },
        {
            "path":r"/admin/moderator/manage_moderator/",
            "permissions":"super"
        },
        {
            "path":r"/admin/moderator/manage_moderator_done/",
            "permissions":"super"
        },
        {
            "path":r"/admin/moderator/add_moderator/",
            "permissions":"super"
        },
        {
            "path":r"/admin/moderator/add_moderator_done/",
            "permissions":"super"
        },
        {
            "path":r"/admin/moderator/delete_moderator/",
            "permissions":"super"
        },
        {
            "path":r"/admin/moderator/delete_moderator_done/",
            "permissions":"super"
        },
        {
            "path":r"/admin/change_password/",
            "permissions":"all"
        },
        {
            "path":r"/admin/change_password_done/",
            "permissions":"all"
        },
        {
            "path":r"/admin/game_setting/",
            "permissions":"submit_setting"
        },
        {
            "path":r"/admin/user/",
            "permissions":"all"
        },
        {
            "path":r"/admin/user/",
            "permissions":"edit_user"
        },        
        {
            "path":r"/admin/makegameconfig/",
            "permissions":"all"
        },         
    
    ],
}

# 管理后台安全校验码
ADMIN_SECRET_KEY='s3avlj$=vk16op_s1g!xyilse9azcu&oh#wln8_@!b+_p7-+@='
