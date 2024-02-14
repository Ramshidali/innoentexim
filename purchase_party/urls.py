from django.urls import path,re_path
from . import views

app_name = 'purchase_party'

urlpatterns = [
    path('list/', views.purchase_party_list, name='purchase_party_list'),
    re_path(r'^info/(?P<pk>.*)/$', views.purchase_party_info, name='purchase_party_info'),
    re_path(r'^create/$', views.create_purchase_party, name='create_purchase_party'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_purchase_party, name='edit_purchase_party'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_purchase_party, name='delete_purchase_party'),
]


