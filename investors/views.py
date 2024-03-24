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
from profit.models import MyProfit
from . models import Investors
from . forms import InvestorsForm, InvestorsEditForm
from main.functions import encrypt_message, generate_form_errors, get_auto_id, paginate, randomnumber, send_email

# Create your views here.
@login_required
@role_required(['superadmin','core_team','director','investor'])
def investors_info(request,pk):
    """
    Investor info
    :param request:
    :return: Investor info view
    """
    instance = Investors.objects.get(pk=pk,is_deleted=False)
    profits = MyProfit.objects.filter(user=instance.user)[:8]

    context = {
        'instance': instance,
        'profits': profits,
        
        'page_name' : 'Investors Info',
        'page_title' : 'Investors Info',
        'is_investors': True,
    }

    return render(request, 'admin_panel/pages/investors/info.html', context)

@login_required
@role_required(['superadmin','core_team','director','investor'])
def investors_list(request):
    """
    Investors listings
    :param request:
    :return: Investors list view
    """
    instances = Investors.objects.filter(is_deleted=False).order_by("-date_added")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(investor_id__icontains=query) 
        )
        title = "Investors - %s" % query
        filter_data['q'] = query

    context = {
        'instances': instances,
        'page_name' : 'Investors',
        'page_title' : 'Investors',
        'filter_data' :filter_data,
        'is_investors' : True,
    }

    return render(request, 'admin_panel/pages/investors/list.html', context)

@login_required
@role_required(['superadmin','core_team','director','investor'])
def create_investor(request):
    """
    create operation of Investors
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = InvestorsForm(request.POST,files=request.FILES)
            
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
                
            user_data = User.objects.create_user(
                username=email,
                password=password,
                is_active=True,
            )
            
            if Group.objects.filter(name="investor").exists():
                group = Group.objects.get(name="investor")
            else:
                group = Group.objects.create(name="investor")

            user_data.groups.add(group)
            
            auto_id = get_auto_id(Investors)
            regid = "IEEII" + str(auto_id).zfill(3)
            
            data = form.save(commit=False)
            data.auto_id = auto_id
            data.creator = request.user
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.investor_id = regid
            data.user = user_data
            data.password = encrypt_message(password)
            data.save()
            
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Investors created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('investors:investors_list')
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
        
        form = InvestorsForm()

        context = {
            'form': form,
            'page_name' : 'Create Investors',
            'page_title' : 'Create Investors',
            'url' : reverse('investors:create_investor'),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_investors' : True,
        }

        return render(request, 'admin_panel/pages/investors/create.html',context)
    
@login_required
@role_required(['superadmin','core_team','director','investor'])
def edit_investor(request,pk):
    """
    edit operation of investor
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(Investors, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = InvestorsEditForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update Investors
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Investors Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('investors:investors_list')
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
        
        form = InvestorsEditForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Investors',
            'page_title' : 'Create Investors',
            'url' : reverse('investors:edit_investor', kwargs={'pk': pk}),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_investors' : True,
        }

        return render(request, 'admin_panel/pages/investors/create.html',context)

@login_required
@role_required(['superadmin','core_team','director','investor'])
def delete_investor(request, pk):
    """
    Investors deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    instance = Investors.objects.get(pk=pk)
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
        "message": "Investors Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('investors:investors_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')