from rest_framework.routers import DefaultRouter
from .views import StatisticsViewSet



router = DefaultRouter()

router.register("", StatisticsViewSet, "statistics")

urlpatterns = [
    
]

urlpatterns += router.urls
