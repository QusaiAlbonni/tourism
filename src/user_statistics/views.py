from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from activities.models import Tour, Listing, Activity, Ticket
from reservations.models import TicketPurchase, Payment, Refund
from app_auth.permissions import isAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from .services import monthly_income, get_net_income_by_section, get_net_income_by_section_monthly
from rest_framework.response import Response

class StatisticsViewSet(ViewSet):
    permission_classes = [IsAuthenticated, isAdmin]
    
    @action(methods=['get'], detail=False)
    def monthly_income_last_year(self, request):
        last_year = timezone.now() - timezone.timedelta(days=365)
        results = monthly_income(last_year)
        return Response(results)
    
    @action(methods=['get'], detail=False)
    def yearly_income_by_section(self, request):
        last_year = timezone.now()
        results = get_net_income_by_section(last_year)
        return Response(results)
    @action(methods=['get'], detail=False)
    def yearly_income_by_section_monthly(self, request):
        last_year = timezone.now()
        results = get_net_income_by_section_monthly(last_year)
        return Response(results)