#standerd
import json
import datetime
from django.conf import settings
#django
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.contrib.auth.models import User,Group
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from dal import autocomplete
#local
from main.decorators import role_required
from . models import CoreTeam
from . forms import CoreTeamEditForm, CoreTeamForm
from main.functions import encrypt_message, generate_form_errors, get_auto_id, paginate, randomnumber, send_email
# Create your views here.

# @login_required
# @role_required(['superadmin'])
# def designation_list(request):
#     """
#     Designation listings
#     :param request:
#     :return: Designation list view
#     """
#     instances = Designation.objects.filter(is_deleted=False).order_by("-id")
    
#     filter_data = {}
#     query = request.GET.get("q")
    
#     if query:

#         instances = instances.filter(
#             Q(auto_id__icontains=query) |
#             Q(name__icontains=query) 
#         )
#         title = "Designations - %s" % query
#         filter_data['q'] = query
    

#     context = {
#         'instances': instances,
#         'page_name' : 'Designations',
#         'page_title' : 'Designations',
#         'filter_data' :filter_data,
#         'is_core_team' : True,
#         'is_core_designation' : True, 
#     }

#     return render(request, 'admin_panel/pages/core_team/designation/list.html', context)

# @login_required
# @role_required(['superadmin'])
# def create_designation(request):
#     """
#     create operation of Designation
#     :param request:
#     :param pk:
#     :return:
#     """
#     if request.method == 'POST':
#         # if instance go to edit
#         form = DesignationForm(request.POST)
            
#         if form.is_valid():
#             data = form.save(commit=False)
#             data.auto_id = get_auto_id(Designation)
#             data.creator = request.user
#             data.date_updated = datetime.datetime.today()
#             data.updater = request.user
#             data.save()

#             response_data = {
#                 "status": "true",
#                 "title": "Successfully Created",
#                 "message": "Designation created successfully.",
#                 'redirect': 'true',
#                 "redirect_url": reverse('core_team:designation_list')
#             }
    
#         else:
#             message =generate_form_errors(form , formset=False)
#             response_data = {
#                 "status": "false",
#                 "title": "Failed",
#                 "message": message,
#             }

#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
#     else:
        
#         form = DesignationForm()

#         context = {
#             'form': form,
#             'page_name' : 'Create Designation',
#             'page_title' : 'Create Designation',
#             'is_core_team' : True,
#             'is_core_designation' : True, 
#         }

#         return render(request, 'admin_panel/pages/core_team/designation/create.html',context)
    
# @login_required
# @role_required(['superadmin'])
# def edit_designation(request,pk):
#     """
#     edit operation of designation
#     :param request:
#     :param pk:
#     :return:
#     """
#     instance = get_object_or_404(Designation, pk=pk)
        
#     message = ''
#     if request.method == 'POST':
#         form = DesignationForm(request.POST,files=request.FILES,instance=instance)
        
#         if form.is_valid():
            
#             #update Designation
#             data = form.save(commit=False)
#             data.date_updated = datetime.datetime.today()
#             data.updater = request.user
#             data.save()
                    
#             response_data = {
#                 "status": "true",
#                 "title": "Successfully Created",
#                 "message": "Designation Update successfully.",
#                 'redirect': 'true',
#                 "redirect_url": reverse('core_team:designation_list'),
#             }
    
#         else:
#             message = generate_form_errors(form ,formset=False)
            
            
#             response_data = {
#                 "status": "false",
#                 "title": "Failed",
#                 "message": message
#             }

#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
#     else:
        
#         form = DesignationForm(instance=instance)

#         context = {
#             'form': form,
#             'page_name' : 'Create Designation',
#             'page_title' : 'Create Designation',
#             'is_core_team' : True,
#             'is_core_designation' : True, 
#         }

#         return render(request, 'admin_panel/pages/core_team/designation/create.html',context)

# @login_required
# @role_required(['superadmin'])
# def delete_designation(request, pk):
#     """
#     Designation deletion, it only mark as is deleted field to true
#     :param request:
#     :param pk:
#     :return:
#     """
#     Designation.objects.filter(pk=pk).update(is_deleted=True)

#     response_data = {
#         "status": "true",
#         "title": "Successfully Deleted",
#         "message": "Designation Successfully Deleted.",
#         "redirect": "true",
#         "redirect_url": reverse('core_team:designation_list'),
#         'is_core_team' : True,
#         'is_core_designation' : True, 
#     }

#     return HttpResponse(json.dumps(response_data), content_type='application/javascript')

@login_required
@role_required(['superadmin','core_team','office_executive','field_executive'])
def core_team(request,pk):
    """
    CoreTeam info
    :param request:
    :return: CoreTeam info view
    """
    instance = CoreTeam.objects.get(pk=pk,is_deleted=False)

    context = {
        'instance': instance,
        'page_name' : 'Core Team',
        'page_title' : 'Core Team',
    }

    return render(request, 'admin_panel/pages/core_team/teams/info.html', context)

@login_required
@role_required(['superadmin'])
def core_team_list(request):
    """
    CoreTeam listings
    :param request:
    :return: CoreTeam list view
    """
    instances = CoreTeam.objects.filter(is_deleted=False).order_by("-date_added")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(employee_id__icontains=query) 
        )
        title = "CoreTeam - %s" % query
        filter_data['q'] = query

    context = {
        'instances': instances,
        'page_name' : 'Core Team',
        'page_title' : 'Core Team',
        'filter_data' :filter_data,
        'is_core_team' : True,
    }

    return render(request, 'admin_panel/pages/core_team/teams/list.html', context)

@login_required
@role_required(['superadmin'])
def create_core_team(request):
    """
    create operation of CoreTeam
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = CoreTeamForm(request.POST)
            
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
                
            user_data = User.objects.create_user(
                username=email,
                password=password,
                is_active=True,
            )
            
            if Group.objects.filter(name="core_team").exists():
                group = Group.objects.get(name="core_team")
            else:
                group = Group.objects.create(name="core_team")

            user_data.groups.add(group)
            
            auto_id = get_auto_id(CoreTeam)
            regid = "IEEIC" + str(auto_id).zfill(3)
            
            data = form.save(commit=False)
            data.auto_id = auto_id
            data.creator = request.user
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.employee_id = regid
            data.user = user_data
            data.password = encrypt_message(password)
            data.save()
            
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "CoreTeam created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('core_team:core_team_list')
            }
        else:
            message =generate_form_errors(form , formset=False)
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        
        form = CoreTeamForm()

        context = {
            'form': form,
            'page_name' : 'Create Core Team',
            'page_title' : 'Create Core Team',
            'url' : reverse('core_team:create_core_team'),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_core_team' : True,
        }

        return render(request, 'admin_panel/pages/core_team/teams/create.html',context)
    
@login_required
@role_required(['superadmin'])
def edit_core_team(request,pk):
    """
    edit operation of core_team
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(CoreTeam, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = CoreTeamEditForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update CoreTeam
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "CoreTeam Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('core_team:core_team_list')
            }
    
        else:
            message = generate_form_errors(form ,formset=False)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        
        form = CoreTeamEditForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Core Team',
            'page_title' : 'Create Core Team',
            'url' : reverse('core_team:edit_core_team', kwargs={'pk': pk}),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_core_team' : True,
        }

        return render(request, 'admin_panel/pages/core_team/teams/create.html',context)

@login_required
@role_required(['superadmin'])
def delete_core_team(request, pk):
    """
    CoreTeam deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    instance = CoreTeam.objects.get(pk=pk)
    current_email = instance.email
    append_email = current_email + str(randomnumber(3)) + "_deleted"
    
    instance.email = append_email
    instance.phone = randomnumber(5)
    instance.is_deleted = True
    instance.save()
    
    user = User.objects.get(username=current_email)
    user.username = append_email
    user.save()
    
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "CoreTeam Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('core_team:core_team_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')