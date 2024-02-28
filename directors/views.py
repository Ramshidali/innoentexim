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
from . models import Departments,Directors
from . forms import *
from main.functions import encrypt_message, generate_form_errors, get_auto_id, has_group, paginate, randomnumber, send_email

# Create your views here.
@login_required
@role_required(['superadmin'])
def department_list(request):
    """
    Department listings
    :param request:
    :return: Department list view
    """
    instances = Departments.objects.filter(is_deleted=False).order_by("-id")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(auto_id__icontains=query) |
            Q(name__icontains=query) 
        )
        title = "Departments - %s" % query
        filter_data['q'] = query
    

    context = {
        'instances': instances,
        'page_name' : 'Departments',
        'page_title' : 'Departments',
        'filter_data' :filter_data,
        'is_directors' : True,
        'is_directors_department' : True, 
    }

    return render(request, 'admin_panel/pages/directors/departments/list.html', context)

@login_required
@role_required(['superadmin'])
def create_department(request):
    """
    create operation of Department
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = DepartmentForm(request.POST)
            
        if form.is_valid():
            data = form.save(commit=False)
            data.auto_id = get_auto_id(Departments)
            data.creator = request.user
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()

            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Department created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('directors:department_list')
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
        
        form = DepartmentForm()

        context = {
            'form': form,
            'page_name' : 'Create Department',
            'page_title' : 'Create Department',
            'is_directors' : True,
            'is_directors_department' : True, 
        }

        return render(request, 'admin_panel/pages/directors/departments/create.html',context)
    
@login_required
@role_required(['superadmin'])
def edit_department(request,pk):
    """
    edit operation of department
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(Departments, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = DepartmentForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            
            #update Department
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Department Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('directors:department_list'),
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
        
        form = DepartmentForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Department',
            'page_title' : 'Create Department',
            'is_directors' : True,
            'is_directors_department' : True, 
        }

        return render(request, 'admin_panel/pages/directors/departments/create.html',context)

@login_required
@role_required(['superadmin'])
def delete_department(request, pk):
    """
    Department deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    Departments.objects.filter(pk=pk).update(is_deleted=True)

    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Department Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('directors:department_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')

@login_required
@role_required(['superadmin','core_team'])
def directors_info(request,pk):
    """
    Director info
    :param request: pk
    :return: Director single view
    """
    user_details = ""
    instance = Directors.objects.get(pk=pk,is_deleted=False)
    
    if has_group(instance.user,"core_team"):
        user_details = CoreTeam.objects.get(user=instance.user)
    elif has_group(instance.user,"investor"):
        user_details = Investors.objects.get(user=instance.user)

    context = {
        'instance': instance,
        'user_details': user_details,
        'page_name' : 'Director Info',
        'page_title' : 'Director Info',
        'is_directors' : True,
        'is_director_page' : True, 
    }

    return render(request, 'admin_panel/pages/directors/info.html', context)

@login_required
@role_required(['superadmin','core_team'])
def directors_list(request):
    """
    Directors listings
    :param request:
    :return: Directors list view
    """
    instances = Directors.objects.filter(is_deleted=False).order_by("-id")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(auto_id__icontains=query) |
            Q(name__icontains=query) 
        )
        title = "Directors - %s" % query
        filter_data['q'] = query
    

    context = {
        'instances': instances,
        'page_name' : 'Directors',
        'page_title' : 'Directors',
        'filter_data' :filter_data,
        'is_directors' : True,
        'is_director_page' : True, 
    }

    return render(request, 'admin_panel/pages/directors/list.html', context)

@login_required
@role_required(['superadmin','core_team'])
def create_director(request):
    """
    create operation of Director
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = DirectorForm(request.POST)
            
        if form.is_valid():
            data = form.save(commit=False)
            data.auto_id = get_auto_id(Directors)
            data.creator = request.user
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
            
            group_names = ["director",form.cleaned_data["department"].name]

            for group_name in group_names:
                if Group.objects.filter(name=group_name).exists():
                    group = Group.objects.get(name=group_name)
                else:
                    group = Group.objects.create(name=group_name)
                User.objects.get(pk=data.user.pk).groups.add(group)
            
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Director created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('directors:directors_list')
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
        
        form = DirectorForm()

        context = {
            'form': form,
            'page_name' : 'Create Director',
            'page_title' : 'Create Director',
            'is_directors' : True,
            'is_director_page' : True, 
        }

        return render(request, 'admin_panel/pages/directors/create.html',context)
    
@login_required
@role_required(['superadmin','core_team'])
def edit_director(request,pk):
    """
    edit operation of director
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(Directors, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = DepartmentForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            
            #update Department
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Department Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('directors:directors_list'),
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
        
        form = DepartmentForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Department',
            'page_title' : 'Create Department',
            'is_directors' : True,
            'is_director_page' : True, 
        }

        return render(request, 'admin_panel/pages/directors/create.html',context)

@login_required
@role_required(['superadmin','core_team'])
def delete_director(request, pk):
    """
    Director deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    Directors.objects.filter(pk=pk).update(is_deleted=True)

    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Director Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('directors:directors_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')