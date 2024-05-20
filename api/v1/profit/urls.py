from django.urls import path, re_path
from . import views

app_name = 'api_v1_profit'

urlpatterns = [
    re_path(r'^profit-dialy/$', views.dialy_profit),
    re_path(r'^profit-monthly/$', views.monthly_profit),
    re_path(r'^profit-my/$', views.my_profit),
]
