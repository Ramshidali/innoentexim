from django.urls import path,re_path
from . import views

app_name = 'other_expences'

urlpatterns = [
    re_path(r'type-list/$', views.other_expence_type_list, name='other_expence_type_list'),
    re_path(r'create-type/$', views.create_other_expence_type, name='create_other_expence_type'),
    re_path(r'^edit-type/(?P<pk>.*)/$', views.edit_other_expence_type, name='edit_other_expence_type'),
    re_path(r'^delete-type/(?P<pk>.*)/$', views.delete_other_expence_type, name='delete_other_expence_type'),
    
    re_path(r'list/$', views.other_expence_list, name='other_expence_list'),
    re_path(r'create/$', views.create_other_expence, name='create_other_expence'),
    re_path(r'^edit/(?P<pk>.*)/$', views.edit_other_expence, name='edit_other_expence'),
    re_path(r'^delete/(?P<pk>.*)/$', views.delete_other_expence, name='delete_other_expence'),
    re_path(r'^print/$', views.print_other_expenses, name='print_other_expenses'),
    re_path(r'^export/$', views.export_other_expenses, name='export_other_expenses'),
]