# # Approval/celery.py
# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Approval.settings')
# app = Celery('Approval')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Helpdesk.settings')

app = Celery('Helpdesk')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
