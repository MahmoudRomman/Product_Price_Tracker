from django.db import models
import uuid 
from django.conf import settings  

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(max_length=500, blank=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Retailer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    base_url = models.URLField()
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductLink(models.Model):
    class CurrencyChoices(models.TextChoices):
        EGP = 'EGP', 'Egyptian Pound'
        USD = 'USD', 'US Dollar'
        EUR = 'EUR', 'Euro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='links')
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE, related_name='product_links')
    url = models.URLField()

    last_known_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.EGP
    )
    available = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    added_by = models.ForeignKey(
            settings.AUTH_USER_MODEL, 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True,
            related_name='added_links'
        )
    
    update_interval_hours = models.IntegerField(default=2)
    next_update_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.product.name} at {self.retailer.name}"


class PriceHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_link = models.ForeignKey(ProductLink, on_delete=models.CASCADE, related_name='history') 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Price Histories"









