#-*- coding: utf-8 -*-
import os
import apps.settings_stg as settings
from django.core.management import setup_environ
setup_environ(settings)

file_list = ['import_test','import_test_stg', 'import_test_dev',
             'settings', 'settings_dev', 'settings_stg', 'manage', 'manage_dev', 'manage_stg']

def run_dir(py_dir):
    for root, dirs, files in os.walk(py_dir):
        if root.find('.svn')==-1:
            for f in files:
                name, ext = os.path.splitext(f)
                if ext == '.py' and name not in file_list:
                    root = root.replace(py_dir, '').replace('/', '.').replace('\\', '.')
                    print 'root',root, 'name',name
                    if root:
                        __import__('apps.' + root, globals(), locals(), [name], -1)
                    else:
                        __import__('apps.' + name, globals(), locals(), [], -1)

if __name__ == '__main__':
    run_dir(settings.BASE_ROOT+'/apps/')
