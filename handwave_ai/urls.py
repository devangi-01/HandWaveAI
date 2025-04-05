"""
URL configuration for handwave_ai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.generic import TemplateView
from sign_language import views
from django.conf import settings
from django.conf.urls.static import static

def homepage(request):
    return render(request, 'index.html')

app_name = "handwave_ai"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('math-solver/', include('math_solver.urls')),
    path('sign-language/', include('sign_language.urls')),
    path('gesture-quiz/', include('gesture_quiz.urls')),
    path('user/', include('user.urls')),  
    path('documentation/', TemplateView.as_view(template_name='documentation.html'), name='documentation'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
