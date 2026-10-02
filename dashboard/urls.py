from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('landing/', views.landing_view, name='landing'),
]

