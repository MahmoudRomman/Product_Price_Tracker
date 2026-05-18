from django.shortcuts import render
from rest_framework.decorators import api_view, APIView, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from .models import Product, Retailer, ProductLink, PriceHistory
from .serializers import ProductSerializer, RetailerSerializer, ProductLinkSerializer, PriceHistorySerializer
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from .permissions import IsAdminOrOwner
from decimal import Decimal, InvalidOperation

from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ProductFilter, ProductLinksFilter, PriceHistoryFilter


class ProductListCreateView(APIView):
    filterset_classes = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsAdminUser()]
        return super().get_permissions()

    def get(self, request):
        queryset = Product.objects.all() # to be paginated later

        backends = [
            DjangoFilterBackend(),
            SearchFilter(),
            OrderingFilter()
        ]

        for backend in backends:
            queryset = backend.filter_queryset(request, queryset, view=self)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveUpdateDestroyAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['DELETE', 'PUT', 'PATCH']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def get_product_object(self, id):
        try:
            return Product.objects.get(id=id)
        except (Product.DoesNotExist, Exception): 
            raise Http404
        
    def get(self, request, id):
        product = self.get_product_object(id)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def patch(self, request, id):
        product = self.get_product_object(id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, id):
        return self.patch(request, id)
    
    def delete(self, request, id):
        product = self.get_product_object(id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class RetailersListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsAdminUser()]
        return super().get_permissions()
    
    def get(self, request):
        retailers = Retailer.objects.all() # to be paginated later
        serializer = RetailerSerializer(retailers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RetailerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RetailersRetrieveUpdateDestroyAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['DELETE', 'PUT', 'PATCH']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def get_retailer_object(self, id):
        try:
            return Retailer.objects.get(id=id)
        except (Retailer.DoesNotExist, Exception): 
            raise Http404
        
    def get(self, request, id):
        retailer = self.get_retailer_object(id)
        serializer = RetailerSerializer(retailer, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def patch(self, request, id):
        retailer = self.get_retailer_object(id)
        serializer = RetailerSerializer(retailer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, id):
        return self.patch(request, id)
    
    def delete(self, request, id):
        retailer = self.get_retailer_object(id)
        retailer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductLinksListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_classes = ProductLinksFilter
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['last_known_price', 'created_at']

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        queryset = ProductLink.objects.filter(product=product)

        backends = [
            DjangoFilterBackend(),
            SearchFilter(),
            OrderingFilter()
        ]

        for backend in backends:
            queryset = backend.filter_queryset(request, queryset, view=self)

        serializer = ProductLinkSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        data = request.data.copy()
        data['product'] = product.id
        
        serializer = ProductLinkSerializer(data=data)
        if serializer.is_valid():
            if ProductLink.objects.filter(product=product, retailer=request.data.get('retailer')).exists():
                return Response(
                    {"error": "This retailer link already exists for this product."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(added_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProductLinksRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsAdminOrOwner]

    def get_object(self, id):
        try:
            return ProductLink.objects.get(id=id)
        except (ProductLink.DoesNotExist, Exception): 
            raise Http404
        
    def get(self, request, id):
        link = self.get_object(id)
        serializer = ProductLinkSerializer(link)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        link = self.get_object(id)
        self.check_object_permissions(request, link)
        
        serializer = ProductLinkSerializer(link, data=request.data, partial=True)
        
        if serializer.is_valid():
            product = serializer.validated_data.get('product', link.product)
            retailer = serializer.validated_data.get('retailer', link.retailer)

            # Check duplication (excluding the current link)
            if ProductLink.objects.filter(product=product, retailer=retailer).exclude(id=id).exists():
                return Response(
                    {"error": "This retailer link already exists for this product."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
        return self.patch(request, id)
    
    def delete(self, request, pk):
        link = self.get_object(pk)
        self.check_object_permissions(request, link)
        
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['PATCH'])
@permission_classes([IsAdminOrOwner])
def update_product_link_price(request, id):
    try:
        link = ProductLink.objects.get(id=id)
    except ProductLink.DoesNotExist:
        return Response({'error': 'ProductLink not found!'}, status=status.HTTP_404_NOT_FOUND)
    
    new_price = request.data.get('last_known_price')
    
    if new_price is None:
        return Response({'error': 'last_known_price is required!'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_price = Decimal(str(new_price))
    except (InvalidOperation, ValueError):
        return Response({'error': 'last_known_price must be a valid number!'}, status=status.HTTP_400_BAD_REQUEST)

    link.last_known_price = new_price
    if 'available' in request.data:
        link.available = request.data.get('available')
    
    link.save()

    return Response({
        'message': 'Price updated successfully!',
        'product': link.product.name,
        'new_price': link.last_known_price
    }, status=status.HTTP_200_OK)



class PriceHistoryListAPIView(APIView):
    permission_classes = [AllowAny]
    filterset_classes = PriceHistoryFilter
    search_fields = ['price']
    ordering_fields = ['timestamp']

    def get(self, request, id):
        try:
            link = ProductLink.objects.get(id=id)
        except (ProductLink.DoesNotExist, Exception):
            raise Http404
        
        queryset = PriceHistory.objects.filter(product_link=link)\
            .select_related('product_link__product', 'product_link__retailer')\
            .order_by('timestamp')
        
        backends = [
            DjangoFilterBackend(),
            SearchFilter(),
            OrderingFilter()
        ]

        for backend in backends:
            queryset = backend.filter_queryset(request, queryset, view=self)
            
        serializer = PriceHistorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
