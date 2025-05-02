from django.urls import path
from .views import *

from  django.contrib.auth import views as auth_views

handeler404 = 'main.views.custom_404_handler'

urlpatterns = [
  path('login/', LoginPage, name='Login'),
  path('register/',RegisterPage, name='Register'),
  path('logout/', Logout, name='Logout'),
  path('email_activation/', ActivationPage, name='Activation'),

  path('activate/<uidb64>/<token>/', Activate, name='activate'),

  path('', Home, name='Home'),
  path('types/', Types, name='types'),
  path('products/<str:type>/', ProductType, name='typeproducts'),
  path('related_products/', searchrelatedProduct, name='related'),
  path('product/<str:pk>/', Products, name='Product'),
  path('download/<str:filename>/', download_file, name='download'),

  path('profile/', Profile, name='profile'),
  path('about/', Aboutus, name='About'),
  path('contact/', ContactPage, name='Contact'),

  path('reset_password/', auth_views.PasswordResetView.as_view(template_name="html/Password_Reset_Form.html"), name="reset_password"),
  path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="html/Password_Reset_Sent.html"), name="password_reset_done"),
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="html/Password_Reset_Confirm.html"), name="password_reset_confirm"),
  path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="html/Password_Reset_Complete.html"), name="password_reset_complete"),
]
