from django.urls import path,re_path
from . import views

app_name = 'exporting'

urlpatterns = [
    re_path(r'export-country-list/$', views.export_countries, name='export_countries'),
    re_path(r'create-export-country/$', views.create_export_country, name='create_export_country'),
    re_path(r'^edit-export-country/(?P<pk>.*)/$', views.edit_export_country, name='edit_export_country'),
    re_path(r'^delete-export-country/(?P<pk>.*)/$', views.delete_export_country, name='delete_export_country'),
    
    re_path(r'^courier-info/(?P<pk>.*)/$', views.courier_partner_info, name='courier_partner_info'),
    re_path(r'courier-List/$', views.courier_partner_list, name='courier_partner_list'),
    re_path(r'^create-courier/$', views.create_courier_partner, name='create_courier_partner'),
    re_path(r'^edit-courier/(?P<pk>.*)/$', views.edit_courier_partner, name='edit_courier_partner'),
    re_path(r'^delete-courier/(?P<pk>.*)/$', views.delete_courier_partner, name='delete_courier_partner'), 
    
    re_path(r'^export-info/(?P<pk>.*)/$', views.exporting, name='exporting'),
    re_path(r'export-List/$', views.exporting_list, name='exporting_list'),
    re_path(r'^create-export/$', views.create_exporting, name='create_exporting'),
    re_path(r'^edit-export/(?P<pk>.*)/$', views.edit_exporting, name='edit_exporting'),
    re_path(r'^delete-export/(?P<pk>.*)/$', views.delete_exporting, name='delete_exporting'),   
    
    re_path(r'export-stock/$', views.export_stock, name='export_stock'),
]


