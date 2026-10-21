from django.contrib import admin
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

# Register your models here.
from .models import Order, Item, TopBuyer
admin.site.register(Order)
admin.site.register(Item)

@admin.register(TopBuyer)
class TopBuyerAdmin(admin.ModelAdmin):
    list_display = ('username', 'movies_purchased', 'orders_placed')
    list_display_links = None

    def get_queryset(self, request):
        return TopBuyer.objects.annotate(
            total_movies=Coalesce(Sum('order__item__quantity'), 0),
            total_orders=Count('order', distinct=True),
        ).filter(total_movies__gt=0)

    
    def get_ordering(self, request):
        return ['-total_movies', 'username']
    @admin.display(description='Movies Purchased', ordering = 'total_movies')
    def movies_purchased(self, obj):
        return obj.total_movies
    @admin.display(description='Orders Placed', ordering = 'total_orders')
    def orders_placed(self, obj):
        return obj.total_orders

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
