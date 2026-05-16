from django.contrib import admin
from .models import Product, Retailer, ProductLink, PriceHistory
# Register your models here.
admin.site.register(Product)
admin.site.register(Retailer)
admin.site.register(ProductLink)
admin.site.register(PriceHistory)

