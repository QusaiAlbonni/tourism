from django.db.models import Sum, F, DecimalField, Subquery, OuterRef, Value
from django.db.models.functions import TruncMonth, Coalesce
from decimal import Decimal
from djmoney.money import Money
from django.utils import timezone
from datetime import timedelta
from reservations.models import Payment, Refund, TicketPurchase
from djmoney.contrib.exchange.models import Rate
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import calendar

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

    
def get_net_income_by_section(timestamp: timezone.datetime):
    
    current_year = timestamp.year    
    
    content_type = ContentType.objects.get_for_model(TicketPurchase)

    rate_subquery = Rate.objects.filter(currency=OuterRef('amount_currency')).values('value')[:1]

    payments = (
        Payment.objects.filter(created__year=current_year)
        .filter(content_type= content_type)
        .filter(reservation__ticket__activity__listing__isnull = True)
        .annotate(
            exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
            amount_usd=F('amount') / F('exchange_rate')
        )
        .aggregate(total_usd=Sum('amount_usd'))
    )

    refunds = (
        Refund.objects.filter(created__year=current_year)
        .filter(content_type= content_type)
        .filter(reservation__ticket__activity__listing__isnull = True)
        .annotate(
            exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
            amount_usd=F('amount') / F('exchange_rate')
        )
        .aggregate(total_usd=Sum('amount_usd'))
    )
    net_income_tours = (payments['total_usd'] or 0) - (refunds['total_usd'] or 0)

    payments = (
        Payment.objects.filter(created__year=current_year)
        .filter(content_type= content_type)
        .filter(reservation__ticket__activity__tour__isnull = True)
        .annotate(
            exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
            amount_usd=F('amount') / F('exchange_rate')
        )
        .aggregate(total_usd=Sum('amount_usd'))
    )

    refunds = (
        Refund.objects.filter(created__year=current_year)
        .filter(content_type= content_type)
        .filter(reservation__ticket__activity__tour__isnull = True)
        .annotate(
            exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
            amount_usd=F('amount') / F('exchange_rate')
        )
        .aggregate(total_usd=Sum('amount_usd'))
    )
    
    net_income_listings = (payments['total_usd'] or 0) - (refunds['total_usd'] or 0)
    
    net_income_properties = 0
    
    
    total = net_income_listings + net_income_tours + net_income_properties
    
    
    return {
        'tour': (net_income_tours / total) * 100,
        'listing': (net_income_listings / total) * 100,
        'properties': (net_income_properties / total) * 100
    }
    
    
def get_net_income_by_section_monthly(timestamp: timezone.datetime):
    current_year = timestamp.year
    content_type = ContentType.objects.get_for_model(TicketPurchase)

    rate_subquery = Rate.objects.filter(currency=OuterRef('amount_currency')).values('value')[:1]

    net_income_by_month = []

    for month in range(1, 13):
        payments_tours = (
            Payment.objects.filter(created__year=current_year, created__month=month)
            .filter(content_type=content_type)
            .filter(reservation__ticket__activity__listing__isnull=True)
            .annotate(
                exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .aggregate(total_usd=Sum('amount_usd'))
        )

        refunds_tours = (
            Refund.objects.filter(created__year=current_year, created__month=month)
            .filter(content_type=content_type)
            .filter(reservation__ticket__activity__listing__isnull=True)
            .annotate(
                exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .aggregate(total_usd=Sum('amount_usd'))
        )

        net_income_tours = (payments_tours['total_usd'] or 0) - (refunds_tours['total_usd'] or 0)

        payments_listings = (
            Payment.objects.filter(created__year=current_year, created__month=month)
            .filter(content_type=content_type)
            .filter(reservation__ticket__activity__tour__isnull=True)
            .annotate(
                exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .aggregate(total_usd=Sum('amount_usd'))
        )

        refunds_listings = (
            Refund.objects.filter(created__year=current_year, created__month=month)
            .filter(content_type=content_type)
            .filter(reservation__ticket__activity__tour__isnull=True)
            .annotate(
                exchange_rate=Coalesce(Subquery(rate_subquery, output_field=DecimalField()), Value(Decimal(1))),
                amount_usd=F('amount') / F('exchange_rate')
            )
            .aggregate(total_usd=Sum('amount_usd'))
        )

        net_income_listings = (payments_listings['total_usd'] or 0) - (refunds_listings['total_usd'] or 0)

        net_income_properties = 0

        net_income_by_month.append({
            'month': calendar.month_name[month],
            'tour': net_income_tours,
            'listing': net_income_listings,
            'properties': net_income_properties
        })

    return net_income_by_month
