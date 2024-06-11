from django.urls import path,re_path
from . import views

app_name = 'sales'

urlpatterns = [  
    re_path(r'get-sales-product-items/$', views.get_sales_product_items, name='get_sales_product_items'),
    re_path(r'item-qty/$', views.sales_item_qty, name='sales_item_qty'),
    
    re_path(r'^info/(?P<pk>.*)/$', views.sales_info, name='sales_info'),
    re_path(r'list/$', views.sales_list, name='sales_list'),
    re_path(r'^create/$', views.create_sales, name='create_sales'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_sales, name='edit_sales'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_sales, name='delete_sales'), 
    re_path(r'^print/$', views.print_sales, name='print_sales'), 
    re_path(r'^export/$', views.export_sales, name='export_sales'),
    
    re_path(r'stock/$', views.sales_stock, name='sales_stock'),
    
    re_path(r'^damage-info/(?P<pk>.*)/$', views.damage_info, name='damage_info'),
    re_path(r'^damage-list/$', views.damage_list, name='damage_list'),
    re_path(r'^damage-create/$', views.create_damage, name='create_damage'),
    re_path(r'^damage-edit/(?P<pk>.*)/$', views.edit_damage, name='edit_damage'),
    re_path(r'^damage-delete/(?P<pk>.*)/$', views.delete_damage, name='delete_damage'), 
    re_path(r'^damage-print/$', views.print_damage, name='print_damage'), 
    re_path(r'^damage-export/$', views.export_damage, name='export_damage'), 
      
    re_path(r'damage-stock/$', views.damage_stock, name='damage_stock'),
]


