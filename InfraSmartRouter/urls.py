"""
URL configuration for InfraSmartRouter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path

from InfraSmartRouter import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    # EC2 instance management
    path('instances/create/', views.create_instance, name='create-instance'),
    path('instances/<int:instance_id>/start/', views.start_instance, name='start-instance'),
    path('instances/<int:instance_id>/stop/', views.stop_instance, name='stop-instance'),
    path('instances/<int:instance_id>/terminate/', views.terminate_instance, name='terminate-instance'),
    path('instances/<int:instance_id>/status/', views.check_instance_status, name='check-instance-status'),
]
