#standerd
import json
import datetime
from django.conf import settings
#django
from django.db.models import Q
from django.urls import reverse
from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
#local
from . forms import *
from . models import *
from main.decorators import role_required
from main.functions import generate_form_errors, get_auto_id

# Create your views here.
@login_required
@role_required(['superadmin','core_team','director'])
def other_expence_type_list(request):
    """
    ExpenceTypes listings
    :param request:
    :return: ExpenceTypes list view
    """
    instances = ExpenceTypes.objects.filter(is_deleted=False).order_by("-id")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(auto_id__icontains=query) |
            Q(name__icontains=query) 
        )
        title = "ExpenceTypes - %s" % query
        filter_data['q'] = query
    

    context = {
        'instances': instances,
        'page_name' : 'Expence Types',
        'page_title' : 'Expence Types',
        'filter_data' :filter_data,
        'is_other_expences' : True,
        'is_other_expence_type_page' : True, 
    }

    return render(request, 'admin_panel/pages/other_expences/types/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def create_other_expence_type(request):
    """
    create operation of ExpenceTypes
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = ExpenceTypesForm(request.POST)
            
        if form.is_valid():
            data = form.save(commit=False)
            data.auto_id = get_auto_id(ExpenceTypes)
            data.creator = request.user
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()

            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Expence Types created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('other_expences:other_expence_type_list')
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
        
        form = ExpenceTypesForm()

        context = {
            'form': form,
            'page_name' : 'Create Expence Types',
            'page_title' : 'Create Expence Types',
            'is_other_expences' : True,
            'is_other_expence_type_page' : True, 
        }

        return render(request, 'admin_panel/pages/other_expences/types/create.html',context)
    
@login_required
@role_required(['superadmin','core_team','director'])
def edit_other_expence_type(request,pk):
    """
    edit operation of other_expences
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(ExpenceTypes, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = ExpenceTypesForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update ExpenceTypes
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Expence Types Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('other_expences:other_expence_type_list'),
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
        
        form = ExpenceTypesForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Expence Types',
            'page_title' : 'Create Expence Types',
            'is_other_expences' : True,
            'is_other_expence_type_page' : True,
        }

        return render(request, 'admin_panel/pages/other_expences/types/create.html',context)

@login_required
@role_required(['superadmin','core_team','director'])
def delete_other_expence_type(request, pk):
    """
    ExpenceTypes deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    ExpenceTypes.objects.filter(pk=pk).update(is_deleted=True)

    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Expence Types Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('other_expences:other_expence_type_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
@role_required(['superadmin','core_team','director'])
def other_expence_list(request):
    """
    OtherExpences listings
    :param request:
    :return: OtherExpences list view
    """
    instances = OtherExpences.objects.filter(is_deleted=False).order_by("-id")
    
    total_amount = instances.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(auto_id__icontains=query) |
            Q(name__icontains=query) 
        )
        title = "ExpenceTypes - %s" % query
        filter_data['q'] = query
    

    context = {
        'instances': instances,
        'total_amount': total_amount,
        'page_name' : 'Other Expence',
        'page_title' : 'Other Expence',
        'filter_data' :filter_data,
        'is_other_expences' : True,
        'is_other_expence_page' : True, 
    }

    return render(request, 'admin_panel/pages/other_expences/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def create_other_expence(request):
    """
    create operation of Other Expence
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = OtherExpencesForm(request.POST)
            
        if form.is_valid():
            data = form.save(commit=False)
            data.auto_id = get_auto_id(OtherExpences)
            data.creator = request.user
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()

            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Expence Types created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('other_expences:other_expence_list')
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
        
        form = OtherExpencesForm()

        context = {
            'form': form,
            'page_name' : 'Create Expence Types',
            'page_title' : 'Create Expence Types',
            'is_other_expences' : True,
            'is_other_expence_page' : True, 
        }

        return render(request, 'admin_panel/pages/other_expences/create.html',context)
    
@login_required
@role_required(['superadmin','core_team','director'])
def edit_other_expence(request,pk):
    """
    edit operation of other_expences
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(OtherExpences, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = OtherExpencesForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update OtherExpences
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Expence Types Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('other_expences:other_expence_list'),
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
        
        form = OtherExpencesForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Expence Types',
            'page_title' : 'Create Expence Types',
            'is_other_expences' : True,
            'is_other_expence_page' : True,
        }

        return render(request, 'admin_panel/pages/other_expences/create.html',context)

@login_required
@role_required(['superadmin','core_team','director'])
def delete_other_expence(request, pk):
    """
    OtherExpences deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    OtherExpences.objects.filter(pk=pk).update(is_deleted=True)

    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Expence Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('other_expences:other_expence_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')