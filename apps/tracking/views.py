from django.shortcuts import render
from rest_framework.decorators import api_view, APIView, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import UserProductTracking, Notification, EmployeeTask
    # استخدام السيريالايزر لتجهيز الداتا
from .serializers import UserProductTrackingSerializer, NotificationSerializer, EmployeeTaskSerializer
from .permissions import IsAdminOrOwner
from apps.products.models import ProductLink, PriceHistory
from apps.products.serializers import ProductLink, PriceHistorySerializer
from django.db.models import Max, Min
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import UserProductTrackingFilter, NotificationsFilter
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class ProductTrackingListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    filterset_classes = UserProductTrackingFilter
    search_fields = ['product_link__product__name', 'product_link__retailer__name']
    ordering_fields = ['created_at']

    def get(self, request):
        queryset = UserProductTracking.objects.filter(user=request.user)

        backends = [
            DjangoFilterBackend(),
            SearchFilter(),
            OrderingFilter()
        ]

        for backend in backends:
            queryset = backend.filter_queryset(request, queryset, view=self)

        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = UserProductTrackingSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    def post(self, request):
        serializer = UserProductTrackingSerializer(data=request.data)
        if serializer.is_valid():
            product_link = serializer.validated_data['product_link']
            if UserProductTracking.objects.filter(user=request.user, product_link=product_link).exists():
                return Response(
                    {"error": "You already tracked this product!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ProductTrackingRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsAdminOrOwner]

    def get_object(self, id):
        try:
            return UserProductTracking.objects.get(id=id)
        except (UserProductTracking.DoesNotExist, Exception): 
            raise Http404
        
    def get(self, request, id):
        tracked_product = self.get_object(id)

        backend = DjangoFilterBackend
        serializer = UserProductTrackingSerializer(tracked_product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        tracked_product = self.get_object(id)
        self.check_object_permissions(request, tracked_product)

        serializer = UserProductTrackingSerializer(tracked_product, data=request.data, partial=True)
        if serializer.is_valid():
            product_link = serializer.validated_data.get('product_link', tracked_product.product_link)

            if UserProductTracking.objects.filter(
                user=request.user, 
                product_link=product_link
            ).exclude(id=id).exists():
                return Response(
                    {"error": "You are already tracking this product link!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
        return self.patch(request, id)
    
    def delete(self, request, id):
        tracked_product = self.get_object(id)
        self.check_object_permissions(request, tracked_product)
        
        tracked_product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    filterset_classes = NotificationsFilter
    
    def get(self, request):
        queryset = Notification.objects.filter(user=request.user).order_by('-sent_at')

        backend = DjangoFilterBackend()
        queryset = backend.filter_queryset(request, queryset, view=self)

        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = NotificationSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            notification = Notification.objects.get(user=request.user, id=id)
        except (Notification.DoesNotExist, Exception): 
            raise Http404
        
        notification.is_read = True
        notification.save()

        return Response({'Mesage: ':'Notification Updated Seccessfully.'}, status=status.HTTP_200_OK)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tracking_statistics(request):
    user = request.user

    unread_notifications_count = Notification.objects.filter(user=user, is_read=False).count()

    tracked_products = UserProductTracking.objects.filter(user=user).select_related(
        'product_link__product', 
        'product_link__retailer'
    )
    total_tracked_products = tracked_products.count()

    biggest_price_drop = None
    max_drop_percentage = -1

    for tracker in tracked_products:
        link = tracker.product_link
        
        price_stats = PriceHistory.objects.filter(product_link=link).aggregate(
            max_price=Max('price')
        )
        
        highest_price = price_stats['max_price']
        current_price = link.last_known_price

        if highest_price and highest_price > 0:
            drop_percent = ((highest_price - current_price) / highest_price) * 100
            
            if drop_percent > max_drop_percentage:
                max_drop_percentage = round(float(drop_percent), 2)
                biggest_price_drop = {
                    'product_name': link.product.name,
                    'retailer_name': link.retailer.name,
                    'highest_price': highest_price,
                    'current_price': current_price,
                    'target_price': tracker.target_price,
                    'drop_percentage': f"{max_drop_percentage}%"
                }

    response_data = {
        'total_tracked_products': total_tracked_products,
        'unread_notifications_count': unread_notifications_count,
        'biggest_price_drop': biggest_price_drop
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([])
def employee_tasks(request):
    tasks = EmployeeTask.objects.filter(
        employee=request.user,
        is_completed=False
    ).select_related(
        'product_link__product', 
        'product_link__retailer'
    ).order_by('-assigned_at')

    if not tasks.exists():
        return Response({'message': 'No pending tasks available for you right now.'}, status=status.HTTP_200_OK)
    

    paginator = StandardResultsSetPagination()
    paginated_tasks = paginator.paginate_queryset(tasks, request)

    serializer = EmployeeTaskSerializer(paginated_tasks, many=True)
    return paginator.get_paginated_response(serializer.data)