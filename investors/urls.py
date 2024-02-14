from django.urls import path,re_path
from . import views

app_name = 'investors'

urlpatterns = [
    path('list/', views.investors_list, name='investors_list'),
    re_path(r'^info/(?P<pk>.*)/$', views.investors_info, name='investors_info'),
    re_path(r'^create/$', views.create_investor, name='create_investor'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_investor, name='edit_investor'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_investor, name='delete_investor'),
]


