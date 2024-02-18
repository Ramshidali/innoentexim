from django.urls import path,re_path
from . import views

app_name = 'sales_party'

urlpatterns = [
    path('list/', views.sales_party_list, name='sales_party_list'),
    re_path(r'^info/(?P<pk>.*)/$', views.sales_party_info, name='sales_party_info'),
    re_path(r'^create/$', views.create_sales_party, name='create_sales_party'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_sales_party, name='edit_sales_party'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_sales_party, name='delete_sales_party'),
]


