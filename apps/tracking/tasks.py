from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, EmployeeTask
from apps.products.models import ProductLink
from apps.users.models import EmployeeShift
from django.http import Http404
from django.utils import timezone



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



@shared_task
def dynamic_link_distribution_task():
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%a').upper() 

    active_shifts = EmployeeShift.objects.filter(
        days__code=current_day,
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_active=True
    ).select_related('employee').distinct()
    
    available_employees = [shift.employee for shift in active_shifts]
    
    if not available_employees:
        print(f"[{now}] - No employees available in the current shift ({current_day} at {current_time}).")
        return

    links_to_update = ProductLink.objects.filter(next_update_at__lte=now)
    
    if not links_to_update.exists():
        print(f"[{now}] - No product links require updating at this time.")
        return

    print(f"Found {links_to_update.count()} links to distribute among {len(available_employees)} employees.")

    emp_count = len(available_employees)
    for index, link in enumerate(links_to_update):
        assigned_emp = available_employees[index % emp_count]
        
        EmployeeTask.objects.update_or_create(
            employee=assigned_emp,
            product_link=link,
            is_completed=False,
            defaults={
                'assigned_at': now 
            }
        )
        
        ProductLink.objects.filter(id=link.id).update(
            next_update_at=now + timezone.timedelta(hours=1)
        )

    return "Distribution completed. Stale tasks refreshed and new tasks assigned!"