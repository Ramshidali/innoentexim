from django.urls import path,re_path
from . import views

app_name = 'core_team'

urlpatterns = [
    # path('designation/', views.designation_list, name='designation_list'),
    # re_path(r'^create-designation/$', views.create_designation, name='create_designation'),
    # re_path(r'^edit-designation/(?P<pk>.*)/$', views.edit_designation, name='edit_designation'),
    # re_path(r'^delete-designation/(?P<pk>.*)/$', views.delete_designation, name='delete_designation'),
    
    path('core_team/', views.core_team_list, name='core_team_list'),
    re_path(r'^coreteam-info/(?P<pk>.*)/$', views.core_team, name='core_team_info'),
    re_path(r'^create-core_team/$', views.create_core_team, name='create_core_team'),
    re_path(r'^edit-core_team/(?P<pk>.*)/$', views.edit_core_team, name='edit_core_team'),
    re_path(r'^delete-core_team/(?P<pk>.*)/$', views.delete_core_team, name='delete_core_team'),
]


