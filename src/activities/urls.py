from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet,activitetagViewSet

router = DefaultRouter()

router.register("guides", GuideViewSet, "guides")
router.register(r'activitetags', activitetagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
