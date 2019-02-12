from __future__ import absolute_import, unicode_literals
from datetime import timedelta
import os

from celery import Celery
from kombu import Exchange, Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopelectro.settings.local')

app = Celery('shopelectro')

# Exchanges
default_exchange = Exchange('default', type='direct')
utils_exchange = Exchange('utils', type='direct')

# http://docs.celeryproject.org/en/latest/userguide/tasks.html
task_queues = (
    Queue(
        name='default',
        exchange=default_exchange,
        routing_key='default',
    ),
    Queue(
        name='mail',
        exchange=utils_exchange,
        routing_key='utils.mail',
    ),
    Queue(
        name='command',
        exchange=utils_exchange,
        routing_key='utils.command',
    )
)

# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
beat_schedule = {
    'update-catalog': {
        'task': 'shopelectro.tasks.update_catalog',
        'schedule': timedelta(hours=2).total_seconds(),
    },
    'check-purchase': {
        'task': 'shopelectro.tasks.check_purchase',
        'schedule': timedelta(days=1).total_seconds(),
    },
}

# http://docs.celeryproject.org/en/master/userguide/routing.html
task_routes = {
    'shopelectro.tasks.update_catalog': {
        'queue': 'command',
        'routing_key': 'utils.command',
        'priority': 30,
    },
    'shopelectro.tasks.check_purchase': {
        'queue': 'command',
        'routing_key': 'utils.command',
        'priority': 20,
    },
    'ecommerce.tasks.send_mail': {
        'queue': 'mail',
        'routing_key': 'utils.mail',
        'priority': 50,
    },
}

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# http://docs.celeryproject.org/en/latest/userguide/configuration.html

BROCKER_URL = (
    f'amqp://{os.environ["RABBITMQ_DEFAULT_USER"]}:{os.environ["RABBITMQ_DEFAULT_PASS"]}'
    f'@{os.environ["RABBITMQ_URL"]}:{os.environ["RABBITMQ_PORT"]}/'
)
app.conf.update(
    broker_url=BROCKER_URL,
    broker_heartbeat=30,
    task_acks_late=True,
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    worker_pool_restarts=True,
    task_routes=task_routes,
    task_queues=task_queues,
    beat_schedule=beat_schedule,
    worker_max_memory_per_child=200000,  # after 250MB will restart
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
