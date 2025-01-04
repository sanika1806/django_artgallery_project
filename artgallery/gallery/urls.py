from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('cart/', views.cart, name='cart'),  # Cart page route
    path('checkout/', views.checkout, name='checkout'),  # Checkout URL
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('order-history/', views.order_history, name='order_history'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('accounts/login/', views.login_view, name='login'),
     path('logout/', views.logout_view, name='logout'),  # Add this route
     
    
    
    

]