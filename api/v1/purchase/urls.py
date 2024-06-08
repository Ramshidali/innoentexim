from django.urls import path, re_path
from . import views

app_name = 'api_v1_purchase'

urlpatterns = [
    re_path(r'^purchase-items/$', views.purchase_items),
    re_path(r'^purchase-parties/$', views.purchase_parties),
    
    re_path(r'^purchase-info/(?P<pk>.*)/$', views.purchase_info),
    re_path(r'^purchase-report/$', views.purchase_report),
    re_path(r'^create-purchase/$', views.create_purchase),
    re_path(r'^delete-purchase/(?P<pk>.*)/$', views.delete_purchase),
]
