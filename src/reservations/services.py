from typing import Any, Mapping, Optional, Type, Union
from django.forms.utils import ErrorList
from service_objects.services import Service
from service_objects import fields
from .models import TicketPurchase, Payment, Refund
from django.db.models import OuterRef, F, Subquery, Sum, DecimalField, ExpressionWrapper
from django.db.models.functions import Cast
from djmoney.money import Money
from decimal import Decimal
from django.db import transaction
from .tasks import send_refund_notifications_task

@transaction.atomic()
def refund_all_purchases(queryset, model):
    purchases = queryset
    
    total_payments_subquery = Payment.objects.filter(
        reservation=OuterRef('pk')
    ).values('reservation').annotate(
        total_sum=Sum('amount')
    ).values('total_sum')
    
    currency_subquery = Payment.objects.filter(
        reservation=OuterRef('pk')
    ).values('amount_currency')[:1]
    
    purchases = purchases.annotate(
        total_payments=Subquery(total_payments_subquery, output_field=DecimalField(max_digits=4, decimal_places=1)),
        refund_rate=Cast(F('ticket__activity__refund_rate') / Decimal(100), output_field=DecimalField(max_digits=4, decimal_places=1)),
        currency=Subquery(currency_subquery)
    ).annotate(
        total_refund=ExpressionWrapper(F('refund_rate') * F('total_payments'), output_field=DecimalField(max_digits=4, decimal_places=1))
    )
    refunds = []
    for purchase in purchases:
        setattr(purchase, 'canceled', True)
        
        total_payments = purchase.total_refund
        currency = purchase.currency
        if total_payments:
            refund = Refund(
                    content_object= purchase,
                    amount        = Money(total_payments.quantize(Decimal('0.00')), currency)
                )
            refunds.append(refund)
    model.objects.bulk_update(purchases, ['canceled'])
    refunds = Refund.objects.bulk_create(refunds)
    
    send_refund_notifications_task.delay([instance.id for instance in refunds])
        
    