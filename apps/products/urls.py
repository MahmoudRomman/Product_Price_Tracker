from django.urls import path
from .views import (
    ProductListCreateView, ProductRetrieveUpdateDestroyAPIView, 
    RetailersListCreateAPIView, RetailersRetrieveUpdateDestroyAPIView,
    ProductLinksListCreateAPIView, ProductLinksRetrieveUpdateDestroyAPIView,
    PriceHistoryListAPIView
    )
urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='products'),
    path('products/<uuid:id>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product_details'),
    path('retailers/', RetailersListCreateAPIView.as_view(), name='retailers'),
    path('retailers/<uuid:id>/', RetailersRetrieveUpdateDestroyAPIView.as_view(), name='retailer_details'),
    path('products/<uuid:product_id>/links/', ProductLinksListCreateAPIView.as_view(), name='product_links'),
    path('product_links/<uuid:id>/', ProductLinksRetrieveUpdateDestroyAPIView.as_view(), name='product_links_details'),
    path('product_links/<uuid:id>/history/', PriceHistoryListAPIView.as_view(), name='product_links_history'),
]