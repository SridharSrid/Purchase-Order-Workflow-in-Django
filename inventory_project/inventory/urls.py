from django.urls import path
# from .views import *
# from . import views

from .views import delete_po
from . import views
from .views import approve_purchase_order, CreatePurchaseOrderView
from django.contrib.auth import views as auth_views
from django.contrib import admin

from .views import create_purchase_order

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

        
    path('admin/', admin.site.urls),
        # Login/logout views
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        # Dashboard (after login)
    path('', views.dashboard, name='inventory/dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-group/', views.add_group, name='add_group'),
    path('assign-user-group/', views.assign_user_group, name='assign_user_group'),
    path('add-group/', views.add_group, name='add_group'),

    path('products/', views.products_view, name='products'),
    path('suppliers/', views.suppliers_view, name='suppliers'),
    path('add-supplier/', views.add_supplier, name='add-supplier'), 
    path('purchase-orders/', views.purchase_orders_view, name='purchase_orders'),
    path('api/purchase-orders/', CreatePurchaseOrderView.as_view(), name='create-purchase-order'),
    path('api/purchase-orders/<int:pk>/approve/', approve_purchase_order, name='approve-purchase-order'),
    path('inventory-transactions/', views.inventory_view, name='inventory_transactions'),

    path('api/purchase-orders/', create_purchase_order, name='create_purchase_order'),
]
