from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import receive_goods, delete_purchase_order, delete_purchase_order_ui, list_purchase_orders

urlpatterns = [
    path('', views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/purchase-orders/', views.create_purchase_order, name='create-purchase-order'),
    path('create-po/', views.create_purchase_order, name='purchase_order_create'),
    path('purchase-order-success/', views.purchase_order_success, name='purchase-order-success'),
    path('api/purchase-orders/<int:pk>/approve/', views.approve_purchase_order, name='approve_purchase_order'),
    path('api/purchase-orders/<int:pk>/reject/', views.reject_purchase_order, name='reject_purchase_order'),
    path('api/purchase-orders/', views.list_purchase_orders, name='list_purchase_orders'),
    path('api/user-info/', views.user_info, name='user_info'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/<int:pk>/approve/', views.approve_po, name='approve_po'),
    path('purchase-orders/<int:pk>/reject/', views.reject_po, name='reject_po'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('api/purchase-orders/<int:pk>/receive/', receive_goods, name='receive_goods'),
    path('purchase-orders/<int:pk>/receive/', views.receive_goods, name='receive_goods'),
    path('purchase-orders/<int:id>/receive-form/', views.receive_goods_form, name='receive_goods_form'),
    path('api/purchase-orders/<int:pk>/', delete_purchase_order, name='purchase_order_delete'),
    path('purchase-orders/delete/<int:pk>/', delete_purchase_order_ui, name='delete_purchase_order_ui'),
    path('api/v2/purchase-orders/', list_purchase_orders, name='purchase_orders_api'),
    path('inventory/', views.product_inventory_view, name='product_inventory'),
    path('suppliers/add/', views.add_supplier, name='add-supplier'),
    path('products/add/', views.add_product, name='add-product'),
]
