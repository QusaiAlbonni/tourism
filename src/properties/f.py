import django_filters.rest_framework.filters as filters
from django_filters.rest_framework import FilterSet
from .models import Property,SupProperty
from services.models import Service
from django.db.models import Count, Avg
from django.db import models
from django.db.models import Q

class ServiceFilter(FilterSet):
    allow_points = filters.BooleanFilter(field_name="allow_points")
    refund = filters.BooleanFilter(method='is_refundable')
    min_points_gift = filters.NumberFilter(field_name="points_gift", lookup_expr='gte')
    discount = filters.BooleanFilter(method='on_discount')
    min_rating = filters.NumberFilter(method='filter_by_rating')
    reservation_period = filters.DateFromToRangeFilter(method='filter_by_reservation_period')

    class Meta:
        model = Service
        fields = []
    def is_refundable(self, queryset, name, value):
        if value >0:
            return queryset.filter(refund_rate__gt=0)
        else:
            return queryset

    def on_discount(self, queryset, name, value):
        if value:
            return queryset.filter(
                id__in=[service.id for service in queryset if service.discount > 6]
            )
        return queryset
    
    def filter_by_rating(self, queryset, name, value):

        queryset = queryset.annotate(avg_ratidng=Avg('servicereview__rating'))
        
        queryset = queryset.filter(avg_ratidng__gte=value)
        return queryset
    

class PropertyFilter(ServiceFilter):
    min_star = filters.NumberFilter(field_name="star", lookup_expr='gte')
    type = filters.ChoiceFilter(field_name="type", choices=Property.PROPERTY_TYPE)
    desgen = filters.ChoiceFilter(field_name="desgen", choices=Property.PROPERTY_DESGEN)
    tags = filters.CharFilter(method='filter_by_tags')
    max_price = filters.NumberFilter(field_name='supproperties__price', lookup_expr='lte', method='filter_by_max_price')
    min_price = filters.NumberFilter(field_name='supproperties__price', lookup_expr='gte', method='filter_by_min_price')
    adults_capacity   = filters.NumberFilter(method='filter_by_adults_capacity')
    children_capacity = filters.NumberFilter(method='filter_by_children_capacity')
    
    class Meta:
        model = Property
        fields = [
    
        ]
    
    def filter_by_tags(self, queryset, name, value):
        tag_ids = [int(tag_id) for tag_id in value.split(',')]

        return queryset.annotate(
        matching_tags_count=Count('property_tags__tag', filter=models.Q(property_tags__tag__id__in=tag_ids))
        ).filter(
            matching_tags_count=len(tag_ids)
        ).distinct()
    
    def filter_by_max_price(self, queryset, name, value):
        return queryset.filter(
            supproperties__price__lte=value
        ).distinct()
    
    def filter_by_min_price(self, queryset, name, value):
        return queryset.filter(
            supproperties__price__gte=value
        ).distinct()

    def filter_by_children_capacity(self, queryset, name, value):
        adults_capacity = self.request.query_params.get('adults_capacity')
        filtered_properties = []
        for property in queryset:
            for sup_property in property.supproperties.all():
                total_capacity = sum(bed.capacity for bed in sup_property.beds.all())
                if total_capacity >= (value+int(adults_capacity)):
                    filtered_properties.append(property)
                    break 
                
        return queryset.filter(id__in=[prop.id for prop in filtered_properties])

    def filter_by_adults_capacity(self, queryset, name, value):
        filtered_properties = []
        for property in queryset:
            for sup_property in property.supproperties.all():
                total_capacity = sum(bed.capacity for bed in sup_property.beds.filter(type__in=['Single', 'Double', 'King']))
                if total_capacity >= value:
                    filtered_properties.append(property)
                    break 
                
        return queryset.filter(id__in=[prop.id for prop in filtered_properties])
    
    def filter_by_reservation_period(self, queryset, name, value):
        start_date = value.start
        end_date = value.stop
        # print(start_date)

        if not start_date or not end_date:
            return queryset
        # print(1)
        qeuryfiltered =queryset.filter(
            Q(supproperties__available_end_date__gte=end_date) &
            Q(supproperties__available_start_date__lte=start_date)
        ).distinct()
        # print(2)
        return qeuryfiltered
        