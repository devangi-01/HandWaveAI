from django.urls import path
from .views import combined_login_register_view
from django.contrib.auth.views import LogoutView

app_name = 'user'
urlpatterns = [

    path('login-register/', combined_login_register_view, name='login'),
     path('logout/', LogoutView.as_view(next_page='user:login'), name='logout'),
    # path('login-register/', combined_login_register_view, name='register'),

]
