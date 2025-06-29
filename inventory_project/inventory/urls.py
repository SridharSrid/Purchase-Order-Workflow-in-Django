from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('api/purchase-orders/', PurchaseOrderCreateView.as_view(), name='create-po'),
    path('api/purchase-orders/list/', PurchaseOrderListView.as_view(), name='list-pos'),
    path('api/purchase-orders/<int:pk>/delete/', delete_po, name='delete-po'),
    path('api/purchase-orders/<int:pk>/approve/', approve_po, name='approve-po'),
    path('api/purchase-orders/<int:pk>/receive/', receive_po, name='receive-po'),
]
