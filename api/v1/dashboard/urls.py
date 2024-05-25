from django.urls import path, re_path
from . import views

app_name = 'api_v1_dashboard'

urlpatterns = [
    re_path(r'^today-status/$', views.today_status),
]
