from celery import shared_task
from tourism.celery import app

@shared_task
def sample_task():
    print('sample')
    return 'sample success'

