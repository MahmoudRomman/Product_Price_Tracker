from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.products.models import ProductLink, PriceHistory
from apps.tracking.models import UserProductTracking, Notification
from .tasks import send_price_alert_email
from datetime import timedelta
from django.utils import timezone


@receiver(post_save, sender=ProductLink)
def handle_price_change(sender, instance, created, **kwargs):
    """
    Once the product_link price changed,
    save a new price_history, push next_update_at, then send notification
    """
    now = timezone.now()

    if created:
        PriceHistory.objects.create(
            product_link=instance,
            price=instance.last_known_price or 0.00,
            is_available=instance.available
        )
        ProductLink.objects.filter(id=instance.id).update(
            next_update_at=now + timedelta(hours=instance.update_interval_hours)
        )
        return

    last_history = PriceHistory.objects.filter(product_link=instance).order_by('-timestamp').first()
    if last_history and last_history.price == instance.last_known_price and last_history.is_available == instance.available:
        return

    PriceHistory.objects.create(
        product_link=instance,
        price=instance.last_known_price,
        is_available=instance.available
    )

    ProductLink.objects.filter(id=instance.id).update(
        next_update_at=now + timedelta(hours=instance.update_interval_hours)
    )

    trackers = UserProductTracking.objects.filter(
        product_link=instance, 
        notification_enabled=True
    )

    for tracker in trackers:
        if tracker.target_price and instance.last_known_price <= tracker.target_price:
            notification = Notification.objects.create(
                user=tracker.user,
                user_product_tracking=tracker,
                message=(
                    f"Great news! The price of {instance.product.name} at {instance.retailer.name} "
                    f"dropped to {instance.last_known_price} {instance.currency}, "
                    f"which is below your target: {tracker.target_price}."
                ),
                price_at_notification=instance.last_known_price
            )
            send_price_alert_email.delay(notification.id)