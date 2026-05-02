from rest_framework import serializers
from .models import Product, Retailer, ProductLink, PriceHistory


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retailer
        fields = ['id', 'name', 'base_url', 'logo_url']

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp', 'is_available']


class ProductLinkSerializer(serializers.ModelSerializer):
    retailer_details = RetailerSerializer(source='retailer', read_only=True)
    
    class Meta:
        model = ProductLink
        fields = [
            'id', 'product', 'retailer', 'retailer_details', 
            'url', 'last_known_price', 'currency', 'available', 'updated_at'
        ]
        extra_kwargs = {
            'retailer': {'write_only': True},
            'product': {'write_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    links = ProductLinkSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'links']

class ProductDetailSerializer(serializers.ModelSerializer):
    # #links is the related_name in ProductLink model
    links = ProductLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'links']