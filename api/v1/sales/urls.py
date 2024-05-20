from django.urls import path, re_path
from . import views

app_name = 'api_v1_sales'

urlpatterns = [
    re_path(r'^sales-parties/$', views.sales_parties),
    re_path(r'^sales-stock/$', views.sales_stock),
    re_path(r'^export-countries/$', views.export_country),
    
    re_path(r'^sales-report/$', views.sales_report),
    re_path(r'^create-sales/$', views.create_sales),
]
