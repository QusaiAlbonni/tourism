from django.utils.module_loading import import_string

from celery import shared_task
from tourism.celery import app

from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend
from djmoney import settings

@shared_task
def update_openexchange_rates(backend=settings.EXCHANGE_BACKEND, **kwargs):
    try:
        backend = import_string(backend)()
        backend.update_rates(**kwargs)
    except Exception as e:
        return e
    return "Success, Exchange rate Updated"