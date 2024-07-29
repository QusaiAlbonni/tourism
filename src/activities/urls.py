from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet, SiteViewSet, TicketViewSet, ActivityViewSet, TourViewSet, TourSiteViewSet, ListingViewSet, ActivityTagViewSet
from rest_framework_nested.routers import NestedSimpleRouter
from reservations.views import TicketPurchaseViewSet

router = DefaultRouter()

router.register("guides", GuideViewSet, "guides")
router.register("sites", SiteViewSet, "sites")
router.register("listings",ListingViewSet, "listings")
router.register("tours", TourViewSet, "tours")
router.register("", ActivityViewSet, "activity")

activities_router = NestedSimpleRouter(router, r'', lookup='activity')
activities_router.register(r'tickets', TicketViewSet, basename='activity-tickets')
activities_router.register(r'tags', ActivityTagViewSet, basename='activity-tags')

tickets_router = NestedSimpleRouter(activities_router, r'tickets', lookup='ticket')
tickets_router.register(r'purchases', TicketPurchaseViewSet, basename='ticket-purchases')

tour_router = NestedSimpleRouter(router, r'tours', lookup= 'tour')
tour_router.register(r'sites', TourSiteViewSet, basename='tour-sites')

urlpatterns = []

urlpatterns += router.urls
urlpatterns += tour_router.urls
urlpatterns += activities_router.urls
urlpatterns += tickets_router.urls
