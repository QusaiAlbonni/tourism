import django_filters.rest_framework.filters as filters
from django_filters.rest_framework import FilterSet
from .models import Activity

class ActivityFilterSet(FilterSet):
    type = filters.CharFilter(method='filter_by_type')

    class Meta:
        model = Activity
        fields = {
            'tour__takeoff_date': ['exact', 'gte', 'lte'],
            'tour__duration': ['exact', 'gte', 'lte'],
            'tickets__price': ['exact', 'gte', 'lte'],
        }
    
    
    def filter_by_type(self, queryset, name, value):
        if value.lower() == 'tour':
            return queryset.filter(tour__isnull=False)
        elif value.lower() == 'listing':
            return queryset.filter(listing__isnull=False)
        return queryset