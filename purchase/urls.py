from django.urls import path,re_path
from . import views

app_name = 'purchase'

urlpatterns = [
    re_path(r'purchase-items/$', views.purchase_items, name='purchase_items'),
    re_path(r'create-purchase-item/$', views.create_purchase_items, name='create_purchase_items'),
    re_path(r'^edit-purchase-item/(?P<pk>.*)/$', views.edit_purchase_item, name='edit_purchase_item'),
    re_path(r'^delete-purchase-item/(?P<pk>.*)/$', views.delete_purchase_items, name='delete_purchase_items'),
    
    re_path(r'^purchase-info/(?P<pk>.*)/$', views.purchase, name='purchase'),
    re_path(r'purchase-List/$', views.purchase_reports, name='purchase_reports'),
    re_path(r'^create-purchase/$', views.create_purchase, name='create_purchase'),
    re_path(r'^edit-purchase/(?P<pk>.*)/$', views.edit_purchase, name='edit_purchase'),
    re_path(r'^delete-purchase/(?P<pk>.*)/$', views.delete_purchase, name='delete_purchase'), 
      
    re_path(r'purchase-stock/$', views.purchase_stock, name='purchase_stock'),
]


