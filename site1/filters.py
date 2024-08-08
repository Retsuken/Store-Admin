import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    STATUS_CHOICES = (
        ('G', 'Продан'),
        ('Y', 'В продаже'),
        ('O', 'Ожидает подтверждение'),
        ('R', 'Не выполнен'),
        ('H', 'Проблемный'),
    )
    
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = Product
        fields = ['status']