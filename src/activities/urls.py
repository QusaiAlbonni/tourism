from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet, ActivityTagViewSet

router = DefaultRouter()

router.register("guides", GuideViewSet, "guides")
router.register(r'tags', ActivityTagViewSet)

urlpatterns = []

urlpatterns += router.urls
