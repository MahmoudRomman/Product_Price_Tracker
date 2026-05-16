from celery import shared_task
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from django.http import Http404


@shared_task
def send_price_alert_email(notification_id):
    try:
        notification = Notification.objects.select_related('user').get(id=notification_id)
        subject = "Price Drop Alert!"

        send_mail(

            subject=subject,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=False,
        )
        return "Email Sent Successfully!"
    except Notification.DoesNotExist:
        pass



