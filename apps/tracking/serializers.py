from rest_framework import serializers
from apps.products.serializers import ProductLinkSerializer
from .models import UserProductTracking, Notification, EmployeeTask



class UserProductTrackingSerializer(serializers.ModelSerializer):
    product_link_details = ProductLinkSerializer(source='product_link', read_only=True)
    product_name = serializers.ReadOnlyField(source='product_link.product.name')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserProductTracking
        fields = [
            'id', 'user', 'product_link', 'product_name', 'product_link_details', 
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



class EmployeeTaskSerializer(serializers.ModelSerializer):
    task_id = serializers.UUIDField(source='id')
    link_id = serializers.UUIDField(source='product_link.id')
    product_name = serializers.CharField(source='product_link.product.name')
    product_image = serializers.URLField(source='product_link.product.image_url')
    retailer_name = serializers.CharField(source='product_link.retailer.name')
    product_link_url = serializers.URLField(source='product_link.url')
    
    product_price = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeTask
        fields = [
            'task_id', 'link_id', 'product_name', 'product_image', 
            'retailer_name', 'product_price', 'product_link_url', 'assigned_at'
        ]

    def get_product_price(self, obj):
        link = obj.product_link
        if link.last_known_price is not None:
            return f"{link.last_known_price} {link.currency}"
        return f"0.00 {link.currency}"