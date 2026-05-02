from django.db import models
from django.conf import settings  
from apps.products.models import ProductLink


class UserProductTracking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='trackings'
    )
    product_link = models.ForeignKey(
        ProductLink, 
        on_delete=models.CASCADE,
        related_name='tracked_by_users'
    )
    target_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notification_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Preventing user to track the same product link twice
        constraints = [
            models.UniqueConstraint(fields=['user', 'product_link'], name='unique_user_product_tracking')
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product_link.product.name}"
    



class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    user_product_tracking = models.ForeignKey(
        UserProductTracking, 
        on_delete=models.CASCADE,
        related_name='tracking_notifications'
    )
    message = models.TextField() 
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    price_at_notification = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Notification for {self.user.email} - {self.sent_at}"