from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound, MethodNotAllowed
from app_auth.permissions import isAdminOrReadOnly, CanManageActivitiesOrReadOnly
from .models import Guide, Activity, Site, Ticket, Tour, TourSite, Listing
from .serializers import GuideSerializer, SiteSerializer, TicketSerializer, ActivitySerializer, TourSerializer, TourSiteSerializer, ListingSerializer, ActivityTagSerializer, ActivityTag
from django.db import transaction
from django.utils.timezone import timedelta, now
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ActivityFilterSet
from app_auth.utils import is_read_only_user
from django.http import Http404
from django.db.models import Q
from django.utils.translation import gettext_lazy as _



class GuideViewSet(viewsets.ModelViewSet):
    serializer_class = GuideSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    def get_queryset(self):
        return Guide.objects.all()
    
    @action(["post"], detail=True, permission_classes= [IsAuthenticated])
    def toggle_like(self, request, pk):
        guide = self.get_object()
        liked = guide.toggle_like(self.request.user)
        return Response({ "liked": liked }, status=status.HTTP_200_OK)
    
class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    queryset = Site.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    def get_queryset(self):
        query = Ticket.objects.filter(activity= self.kwargs['activity_pk'])
        if not(self.request.user.is_authenticated) or not(self.request.user.is_admin or self.request.user.is_staff or self.request.user.has_perm('app_auth.manage_activities')):
            query = query.filter(valid_until__gte=now(), activity__canceled = False)
        return query
            
    def get_serializer_context(self):   
        context = super().get_serializer_context()
        context['activity_pk'] = self.kwargs['activity_pk']
        return context
    
    @action(['post',], detail=True)
    def cancel(self, request, pk, **kwargs):
        obj = Ticket.objects.get(pk= pk)
        if obj.canceled:
            raise ValidationError({'detail':_('already canceled')})
        if hasattr(obj.activity, 'tour'):
            if obj.activity.tour.takeoff_date_before_now():
                raise ValidationError({'detail':_('tour has already begun or concluded')})        
        obj.canceled = True
        obj.save()
        return Response({'detail':'success'}, status.HTTP_200_OK)

    @action(['post',], True)
    def refund_all(self, request, activity_pk, pk):
        obj = Ticket.objects.get(pk= pk, activity_id = activity_pk)
        obj.refund_all()
        return Response({'detail':'success'}, status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.purchases.filter(refunds__isnull= False, canceled=False).exists():
            raise ValidationError({'detail':_('cannot delete while some users have not been refunded')})
        return super().destroy(request, *args, **kwargs)
    
    
    
class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
                    '@name',
                    '@description',
                    '@name_en',
                    '@description_en',
                    '@tour__guide__name',
                    '@tickets__name',
                    '@tour__sites__name',
                    '@listing__site__name',
                    '@listing__site__address__locality__state__country__name',
                    '@listing__site__address__locality__state__name',
                    '@tour__sites__address__locality__state__country__name',
                    '@tour__sites__address__locality__state__name',
                    '@listing__site__address__raw',
                    '@tour__sites__address__raw',
                    ]
    filterset_class= ActivityFilterSet
    
    def get_queryset(self):
        queryset = self.queryset
        if is_read_only_user(self.request.user, 'app_auth.manage_activities'):
            queryset = queryset.filter(canceled = False)
            queryset = queryset.filter(Q(tour__isnull = True) | Q(tour__tour_sites__isnull = False))
        return queryset
    
    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    
    @action(['post',], detail=True)
    def cancel(self, request, pk):
        obj = Activity.objects.get(pk= pk)
        if obj.canceled:
            raise ValidationError({'detail':'already canceled'})
        if hasattr(obj, 'tour'):
            if obj.tour.takeoff_date_before_now():
                raise ValidationError({'detail':_('tour has already begun or concluded')})
            

        obj.canceled = True
        obj.save()
        return Response({'detail':'success'}, status.HTTP_200_OK)
    @action(['post',], True)
    def refund_all(self, request, pk):
        obj = Activity.objects.get(pk= pk)
        obj.refund_all()
        return Response({'detail':'success'}, status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        
        for ticket in obj.tickets.all():
            if ticket.purchases.filter(refunds__isnull= False, canceled=False).exists():
                raise ValidationError({'detail':_('cannot delete while some users have not been refunded')})
        return super().destroy(request, *args, **kwargs)
    
    

class TourViewSet(viewsets.ModelViewSet):
    serializer_class = TourSerializer
    queryset = Tour.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    
    def get_queryset(self):
        queryset = self.queryset
        if is_read_only_user(self.request.user, 'app_auth.manage_activities'):
            queryset = queryset.filter(canceled = False)
            queryset = queryset.filter(tour_sites__isnull = False)
        return queryset
            
        
    
class TourSiteViewSet(viewsets.ModelViewSet):
    serializer_class  = TourSiteSerializer
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    def get_queryset(self):
        return TourSite.objects.filter(tour= self.kwargs['tour_pk'])
    def get_serializer_context(self):   
        context = super().get_serializer_context()
        context['tour_pk'] = self.kwargs['tour_pk']
        return context
    @action(['post'], False)
    def swap_order(self, request, *args, **kwargs):
        first_attraction_id = request.data.get('first_site_id')
        second_attraction_id = request.data.get('second_site_id')
        if not first_attraction_id or not second_attraction_id:
            raise ValidationError({'detail': _('either the first id or second one or both was left blank')})
        first_attraction = self.get_queryset().filter(site_id=first_attraction_id).exists()
        second_attraction = self.get_queryset().filter(site_id=second_attraction_id).exists()
        if not first_attraction or not second_attraction:
            raise NotFound({'detail': _('Not Found')})
        
        
        with transaction.atomic():
            first_attraction = self.get_queryset().get(site_id=first_attraction_id)
            second_attraction = self.get_queryset().get(site_id=second_attraction_id)

            first_order = first_attraction.order
            second_order = second_attraction.order
            
            first_attraction.order = 0
            first_attraction.save()
            
            second_attraction.order = first_order
            second_attraction.save()
            
            first_attraction.order = second_order
            first_attraction.save()
        serializer = TourSiteSerializer([first_attraction, second_attraction], many=True, read_only= True)
        return Response(serializer.data, status.HTTP_200_OK)
        
        
class ActivityTagViewSet(viewsets.ModelViewSet):
    serializer_class  = ActivityTagSerializer
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    def get_queryset(self):
        return ActivityTag.objects.filter(activity= self.kwargs['activity_pk'])
    def get_serializer_context(self):   
        context = super().get_serializer_context()
        context['activity_pk'] = self.kwargs['activity_pk']
        return context
class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    
    def get_queryset(self):
        queryset = self.queryset
        if is_read_only_user(self.request.user, 'app_auth.manage_activities'):
            queryset = queryset.filter(canceled = False)
        return queryset
    