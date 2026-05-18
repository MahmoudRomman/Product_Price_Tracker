import django_filters
from .models import Product, ProductLink, PriceHistory

class ProductFilter(django_filters.FilterSet):

    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'contains'],
        }

class ProductLinksFilter(django_filters.FilterSet):
    class Meta:
        model = ProductLink
        fields = {
            'retailer__name': ['iexact', 'contains'],
            'currency': ['iexact', 'contains'],
            'available': ['exact'],
        }


class PriceHistoryFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = PriceHistory
        fields = []

