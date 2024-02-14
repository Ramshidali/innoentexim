from django.urls import path,re_path
from . import views

app_name = 'executive'

urlpatterns = [
    path('list/', views.executive_list, name='executive_list'),
    re_path(r'^info/(?P<pk>.*)/$', views.executive_info, name='executive_info'),
    re_path(r'^create/$', views.create_executive, name='create_executive'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_executive, name='edit_executive'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_executive, name='delete_executive'),
]


