from django.urls import path
from .views import combined_login_register_view

app_name = 'user'
urlpatterns = [

    path('login-register/', combined_login_register_view, name='login'),
    # path('login-register/', combined_login_register_view, name='register'),

]
