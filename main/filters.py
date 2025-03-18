import django_filters
from  .models import Product

class ProductListFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    class Meta:
        model = Product
        fields = ['category','price_min','price_max']
