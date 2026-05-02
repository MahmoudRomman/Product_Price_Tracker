from rest_framework import serializers
from apps.tracking.models import UserProductTracking, Notification
from apps.products.serializers import ProductLinkSerializer
from apps.users.serializers import UserProductTracking, Notification



class UserProductTrackingSerializer(serializers.ModelSerializer):
    product_link_details = ProductLinkSerializer(source='product_link', read_only=True)

    class Meta:
        model = UserProductTracking
        fields = [
            'id', 'user', 'product_link', 'product_link_details', 
            'target_price', 'notification_enabled', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'product_link': {'write_only': True},
            'user': {'read_only': True}
        }


class NotificationSerializer(serializers.ModelSerializer):
    tracking_details = UserProductTrackingSerializer(source='user_product_tracking', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_product_tracking', 'tracking_details', 
            'message', 'sent_at', 'is_read', 'price_at_notification'
        ]
        extra_kwargs = {
            'user_product_tracking': {'write_only': True}
        }