from django.urls import path,re_path
from . import views

app_name = 'directors'

urlpatterns = [
    path('department-list/', views.department_list, name='department_list'),
    re_path(r'^create-department/$', views.create_department, name='create_department'),
    re_path(r'^edit-department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    re_path(r'^delete-department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
    
    path('directors-list/', views.directors_list, name='directors_list'),
    re_path(r'^create-director/$', views.create_director, name='create_director'),
    re_path(r'^info-director/(?P<pk>.*)/$', views.directors_info, name='directors_info'),
    re_path(r'^edit-director/(?P<pk>.*)/$', views.edit_director, name='edit_director'),
    re_path(r'^delete-director/(?P<pk>.*)/$', views.delete_director, name='delete_director'),
]
