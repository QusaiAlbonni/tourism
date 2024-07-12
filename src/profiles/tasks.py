from celery import shared_task
from tourism.celery import app
from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend

@shared_task
def update_openexchange_rates():
    try:
        OpenExchangeRatesBackend().update_rates()
    except:
        return "FAILED"
    return "Success, Exchange rate Updated"