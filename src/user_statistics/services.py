from django.db.models import Sum, F, DecimalField, Subquery, OuterRef
from django.db.models.functions import TruncMonth
from decimal import Decimal
from djmoney.money import Money
from django.utils import timezone
from datetime import timedelta
from reservations.models import Payment, Refund
from djmoney.contrib.exchange.models import Rate
from django.utils import timezone

def monthly_income(timestamp):

        rate_subquery = Rate.objects.filter(currency=OuterRef('amount_currency')).values('value')[:1]

        payments = (
            Payment.objects.filter(created__gte=timestamp)
            .annotate(month=TruncMonth('created'))
            .annotate(
                exchange_rate=Subquery(rate_subquery, output_field=DecimalField()),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .values('month')
            .annotate(total_usd=Sum('amount_usd'))
            .order_by('month')
        )

        refunds = (
            Refund.objects.filter(created__gte=timestamp)
            .annotate(month=TruncMonth('created'))
            .annotate(
                exchange_rate=Subquery(rate_subquery, output_field=DecimalField()),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .values('month')
            .annotate(total_usd=Sum('amount_usd'))
            .order_by('month')
        )

        # Calculate net payments by subtracting refunds from payments
        net_totals = {}
        for payment in payments:
            month = payment['month']
            net_totals[month] = payment['total_usd']

        for refund in refunds:
            month = refund['month']
            if month in net_totals:
                net_totals[month] -= refund['total_usd']
            else:
                net_totals[month] = -refund['total_usd']

        # Convert the net_totals dictionary into a list of (month, net_total) tuples
        result = [{'month':month.date(), 'total' : net_total} for month, net_total in net_totals.items()]
        result.sort(key=lambda x: x['month'])  # Sort by month

        return result
    
def income_by_section(timestamp):

        rate_subquery = Rate.objects.filter(currency=OuterRef('amount_currency')).values('value')[:1]

        payments = (
            Payment.objects.filter(created__gte=timestamp)
            .annotate(month=TruncMonth('created'))
            .annotate(
                exchange_rate=Subquery(rate_subquery, output_field=DecimalField()),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .values('month')
            .annotate(total_usd=Sum('amount_usd'))
            .order_by('month')
        )

        refunds = (
            Refund.objects.filter(created__gte=timestamp)
            .annotate(month=TruncMonth('created'))
            .annotate(
                exchange_rate=Subquery(rate_subquery, output_field=DecimalField()),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .values('month')
            .annotate(total_usd=Sum('amount_usd'))
            .order_by('month')
        )

        # Calculate net payments by subtracting refunds from payments
        net_totals = {}
        for payment in payments:
            month = payment['month']
            net_totals[month] = payment['total_usd']

        for refund in refunds:
            month = refund['month']
            if month in net_totals:
                net_totals[month] -= refund['total_usd']
            else:
                net_totals[month] = -refund['total_usd']

        # Convert the net_totals dictionary into a list of (month, net_total) tuples
        result = [{'month':month.date(), 'total' : net_total} for month, net_total in net_totals.items()]
        result.sort(key=lambda x: x['month'])  # Sort by month

        return result
    
def get_net_income_by_section(timestamp: timezone.datetime, section):
    
    kwargs = {
        section + "__isnull": False
    }
    current_year = timestamp.year

    rate_subquery = Rate.objects.filter(currency=OuterRef('amount_currency')).values('value')[:1]

    payments = (
        Payment.objects.filter(created__year=current_year)
        .filter(**kwargs)
        .annotate(
            exchange_rate=Subquery(rate_subquery, output_field=DecimalField()),
            amount_usd=F('amount') / F('exchange_rate')
        )
        .aggregate(total_usd=Sum('amount_usd'))
    )

    refunds = (
        Refund.objects.filter(created__year=current_year)
        .filter(**kwargs)
        .annotate(
            exchange_rate=Subquery(rate_subquery, output_field=DecimalField()),
            amount_usd=F('amount') / F('exchange_rate')
        )
        .aggregate(total_usd=Sum('amount_usd'))
    )
    net_income = (payments['total_usd'] or 0) - (refunds['total_usd'] or 0)

    return net_income
    
