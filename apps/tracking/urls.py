from django.urls import path
from .views import (
    ProductTrackingListCreateAPIView, ProductTrackingRetrieveUpdateDestroyAPIView,
    NotificationListAPIView, NotificationReadAPIView, tracking_statistics,
)

urlpatterns = [
    path('my_tracking/', ProductTrackingListCreateAPIView.as_view(), name='tracked_products'),
    path('my_tracking/<uuid:id>/', ProductTrackingRetrieveUpdateDestroyAPIView.as_view(), name='tracked_product_details'),
    path('my_notifications/', NotificationListAPIView.as_view(), name='notifications'),
    path('my_notifications/<uuid:id>/mark_read/', NotificationReadAPIView.as_view(), name='notification_readed'),

    path('my_stats/', tracking_statistics, name='tracking_statistics'),

]

