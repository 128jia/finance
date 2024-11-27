from django.urls import path
from . import views

urlpatterns = [
    path('', views.web),
    path('run_distance/', views.ScreenerDistance),
    #########hw2#
    #path('ajax_data/', views.ajax_data),
    path('rsi_cross_ajax/', views.rsi_cross_ajax),
    path('run_strategy/', views.run_strategy),
    
]