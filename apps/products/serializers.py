from rest_framework import serializers
from .models import Product, Retailer, ProductLink, PriceHistory


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retailer
        fields = ['id', 'name', 'base_url', 'logo_url', 'created_at']
        extra_kwargs = {
            'retailer': {'write_only': True},
            'product': {'write_only': True}
        }
        extra_kwargs = {
            'created_at': {'read_only': True},
        }



class ProductLinkSerializer(serializers.ModelSerializer):
    retailer_details = RetailerSerializer(source='retailer', read_only=True)
    created_by = serializers.CharField(source='added_by.username', read_only=True)
    class Meta:
        model = ProductLink
        fields = [
            'id', 'product', 'retailer', 'retailer_details', 'added_by', 'created_by',
            'url', 'last_known_price', 'currency', 'available', 'updated_at'
        ]
        extra_kwargs = {
            'retailer': {'write_only': True},
            'product': {'write_only': True},
            'added_by': {'write_only': True},
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'created_at']

class ProductDetailSerializer(serializers.ModelSerializer):
    # #links is the related_name in ProductLink model
    links = ProductLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'links']


class PriceHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_link.product.name')
    retailer_name = serializers.CharField(source='product_link.retailer.name')
    class Meta:
        model = PriceHistory
        fields = ['id', 'product_name', 'retailer_name', 'price', 'timestamp', 'is_available']