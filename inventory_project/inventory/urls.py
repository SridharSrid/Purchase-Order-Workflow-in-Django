from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import custom_login_view
from .views import CustomAuthToken

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    #  path('', custom_login_view, name='login'),
    #  path('', views.login_page, name='login-page'),
    # path('login.html', views.login_page, name='login'),
    #  path('api/login/', CustomAuthToken.as_view(), name='api-login'),
     
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/purchase-orders/', views.create_purchase_order, name='create-purchase-order'),
    path('create-po/', views.create_po, name='create_po'),
    path('purchase-order-success/', views.purchase_order_success, name='purchase_order_success'),
    path('api/purchase-orders/<int:pk>/approve/', views.approve_purchase_order, name='approve_purchase_order'),
    path('api/purchase-orders/<int:pk>/reject/', views.reject_purchase_order, name='reject_purchase_order'),
    path('api/purchase-orders/', views.list_purchase_orders, name='list_purchase_orders'),
    path('api/user-info/', views.user_info, name='user_info'),

    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/<int:pk>/approve/', views.approve_po, name='approve_po'),
    path('purchase-orders/<int:pk>/reject/', views.reject_po, name='reject_po'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
]
