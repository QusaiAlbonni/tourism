from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet, SiteViewSet, TicketViewSet, ActivityViewSet, TourViewSet, TourSiteViewSet, ListingViewSet
from rest_framework_nested.routers import NestedSimpleRouter

router = DefaultRouter()

router.register("guides", GuideViewSet, "guides")
router.register("sites", SiteViewSet, "sites")
router.register("listings",ListingViewSet, "listings")
router.register("tours", TourViewSet, "tours")
router.register("", ActivityViewSet, "activity")

activities_router = NestedSimpleRouter(router, r'', lookup='activity')
activities_router.register(r'tickets', TicketViewSet, basename='activity-tickets')

tour_router = NestedSimpleRouter(router, r'tours', lookup= 'tour')
tour_router.register(r'sites', TourSiteViewSet, basename='tour-sites')

urlpatterns = []

urlpatterns += router.urls
urlpatterns += tour_router.urls
urlpatterns += activities_router.urls
