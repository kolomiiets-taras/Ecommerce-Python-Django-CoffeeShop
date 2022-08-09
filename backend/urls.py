from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('add_item/<str:pk>/', views.add_item, name='add_item'),
    path('checkout/<str:order_id>/', views.checkout, name='checkout'),
    path('success_page/', views.success_page, name='success_page'),
    path('product/<str:pk>/', views.product, name="product"),
    path('get_cart_number/', views.get_cart_number, name='get_cart_number'),

    path('minus_quantity/<str:pk>/', views.minus_quantity, name='minus_quantity'),
    path('plus_quantity/<str:pk>/', views.plus_quantity, name='plus_quantity'),
    path('remove_item/<str:pk>/', views.remove_item, name='remove_item'),

    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('create_password/', views.create_password, name='create_password'),
    path('user_page/', views.user_page, name='user_page'),
    path('order_copy/<str:pk>/', views.order_copy, name='order_copy'),

]