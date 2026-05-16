from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.products.models import ProductLink, PriceHistory
from apps.tracking.models import UserProductTracking, Notification
from .tasks import send_price_alert_email


@receiver(post_save, sender=ProductLink)
def handle_price_change(sender, instance, created, **kwargs):
    """
    Once the product_link price changed,
    save a new price_history then, send notification
    """

    # If the product_link is created right now, record a new PriceHistory intance then return
    if created:
        PriceHistory.objects.create(
            product_link=instance,
            price=instance.last_known_price,
            is_available=instance.available
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