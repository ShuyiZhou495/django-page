"""calibration_methods URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from calibration import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('add_config/', views.Add_config.as_view(), name='add_config'),
    path('running/<int:config_id>', views.Running.as_view(), name='running'),
    path('admin/', admin.site.urls),
]
