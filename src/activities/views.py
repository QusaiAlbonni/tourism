from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from app_auth.permissions import isAdminOrReadOnly, CanManageActivitiesOrReadOnly
from .models import Guide, Activity, Site, Ticket, Tour, TourSite, Listing
from .serializers import GuideSerializer, SiteSerializer, TicketSerializer, ActivitySerializer, TourSerializer, TourSiteSerializer, ListingSerializer
from django.db import transaction



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
        return Ticket.objects.filter(activity= self.kwargs['activity_pk'])
    def get_serializer_context(self):   
        context = super().get_serializer_context()
        context['activity_pk'] = self.kwargs['activity_pk']
        return context
    
    
class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    

class TourViewSet(viewsets.ModelViewSet):
    serializer_class = TourSerializer
    queryset = Tour.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    
class TourSiteViewSet(viewsets.ModelViewSet):
    serializer_class = TourSiteSerializer
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
            raise ValidationError({'detail': 'either the first id or second one or both was left blank'})
        first_attraction = self.get_queryset().filter(site_id=first_attraction_id).exists()
        second_attraction = self.get_queryset().filter(site_id=second_attraction_id).exists()
        if not first_attraction or not second_attraction:
            raise NotFound({'detail': 'Not Found'})
        
        
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
        
class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()
    permission_classes= [IsAuthenticatedOrReadOnly, CanManageActivitiesOrReadOnly]
    