from django.urls import path
# from .views import *
# from . import views

from .views import delete_po
from . import views
from .views import approve_purchase_order, CreatePurchaseOrderView

# urlpatterns = [
#     path('api/purchase-orders/', PurchaseOrderCreateView.as_view(), name='create-po'),
#     path('api/purchase-orders/list/', PurchaseOrderListView.as_view(), name='list-pos'),
#     path('api/purchase-orders/<int:pk>/delete/', delete_po, name='delete-po'),
#     path('api/purchase-orders/<int:pk>/approve/', approve_po, name='approve-po'),
#     path('api/purchase-orders/<int:pk>/receive/', approve_po, name='receive-po'),
#     path('api/purchase-orders/', list_purchase_orders, name='list-pos'),
# ]
urlpatterns = [
    # path('api/purchase-orders/', views.list_pos, name='list-pos'),
    # path('api/purchase-orders/', views.create_po, name='create-po'),
    # path('api/purchase-orders/<int:pk>/approve/', views.approve_po, name='approve-po'),
    # path('api/purchase-orders/<int:pk>/receive/', receive_goods, name='receive-goods'),
    path('api/purchase-orders/<int:pk>/', delete_po, name='delete-po'),
    # path('purchase-orders/', views.list_purchase_orders, name='purchase-orders'),

    path('products/', views.products_view, name='products'),
    path('suppliers/', views.suppliers_view, name='suppliers'),
    path('add-supplier/', views.add_supplier, name='add-supplier'), 
    path('purchase-orders/', views.purchase_orders_view, name='purchase_orders'),
    path('api/purchase-orders/', CreatePurchaseOrderView.as_view(), name='create-purchase-order'),
    path('api/purchase-orders/<int:pk>/approve/', approve_purchase_order, name='approve-purchase-order'),
    path('inventory-transactions/', views.inventory_view, name='inventory_transactions'),
]
