from django.urls import path,re_path
from . import views

app_name = 'profit'

urlpatterns = [
    re_path(r'^calculate-dialy-profit/(?P<date>.*)/$', views.calculate_profit, name='calculate_profit'),
    
    path('exchange-rate-list/', views.exchange_rates, name='exchange_rates'),
    re_path(r'^exchange-rate-create/$', views.create_exchange_rate, name='create_exchange_rate'),
    re_path(r'^exchange-rate-edit/(?P<pk>.*)/$', views.edit_exchange_rate, name='edit_exchange_rate'),
    re_path(r'^exchange-rate-delete/(?P<pk>.*)/$', views.delete_exchange_rate, name='delete_exchange_rate'),
    re_path(r'^print-exchange-rate/$', views.print_exchange_rates, name='print_exchange_rates'),
    re_path(r'^export-exchange-rate/$', views.export_exchange_rates, name='export_exchange_rates'),
    
    path('dialy-profit-list/', views.dialy_profits, name='dialy_profits'),
    path('print-dialy-profit-list/', views.print_dialy_profits, name='print_dialy_profits'),
    path('export-dialy-profit/', views.export_dialy_profits, name='export_dialy_profits'),
    
    path('monthly-profit-list/', views.monthly_profits, name='monthly_profits'),
    path('print-monthly-profit-list/', views.print_monthly_profits, name='print_monthly_profits'),
    path('export-monthly-profit/', views.export_monthly_profits, name='export_monthly_profits'),
    
    path('my-profit-list/', views.users_profits, name='users_profits'),
    path('print-my-profit-list/', views.print_my_profits, name='print_my_profits'),
    path('export-my-profit/', views.export_my_profits, name='export_my_profits'),
]