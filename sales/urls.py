from django.urls import path,re_path
from . import views

app_name = 'sales'

urlpatterns = [  
    re_path(r'item-qty/$', views.sales_item_qty, name='sales_item_qty'),
    
    re_path(r'^info/(?P<pk>.*)/$', views.sales_info, name='sales_info'),
    re_path(r'List/$', views.sales_list, name='sales_list'),
    re_path(r'^create/$', views.create_sales, name='create_sales'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_sales, name='edit_sales'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_sales, name='delete_sales'), 
      
    re_path(r'stock/$', views.sales_stock, name='sales_stock'),
]


