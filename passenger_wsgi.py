# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u2280704/data/www/test-website3.ru/site_bk')
sys.path.insert(1, '/var/www/u2280704/data/djangoenv2/lib/python3.9/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'site_bk.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()