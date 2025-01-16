from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('ajax_data/', views.ajax_data),
    path('inductor/', views.inductor, name='inductor'),
]