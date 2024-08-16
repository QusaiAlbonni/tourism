from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from activities.models import Tour, Listing, Activity, Ticket
from reservations.models import TicketPurchase, Payment, Refund
from app_auth.permissions import isAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from .services import monthly_income
from rest_framework.response import Response

class StatisticsViewSet(ViewSet):
    permission_classes = [IsAuthenticated, isAdmin]
    
    @action(methods=['get'], detail=False)
    def monthly_income_last_year(self, request):
        last_year = timezone.now() - timezone.timedelta(days=365)
        results = monthly_income(last_year)
        return Response(results)