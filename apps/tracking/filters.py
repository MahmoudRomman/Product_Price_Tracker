import django_filters


import django_filters
from .models import UserProductTracking, Notification

class UserProductTrackingFilter(django_filters.FilterSet):

    class Meta:
        model = UserProductTracking
        fields = {
            'notification_enabled': ['exact'],
        }

class NotificationsFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Notification
        fields = {
            'is_read': ['exact'],
        }
