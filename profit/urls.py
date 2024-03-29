from django.urls import path,re_path
from . import views

app_name = 'profit'

urlpatterns = [
    re_path(r'^calculate-dialy-profit/(?P<date>.*)/$', views.calculate_profit, name='calculate_profit'),
    
    path('list/', views.exchange_rates, name='exchange_rates'),
    re_path(r'^create/$', views.create_exchange_rate, name='create_exchange_rate'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_exchange_rate, name='edit_exchange_rate'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_exchange_rate, name='delete_exchange_rate'),
    
    path('dialy-profit-list/', views.dialy_profits, name='dialy_profits'),
    path('monthly-profit-list/', views.monthly_profits, name='monthly_profits'),
    path('my-profit-list/', views.users_profits, name='users_profits'),
]