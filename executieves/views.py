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
from django.db import transaction, IntegrityError
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from dal import autocomplete
#local
from main.decorators import role_required
from . models import Executive
from . forms import ExecutiveForm, ExecutiveEditForm
from main.functions import encrypt_message, generate_form_errors, get_auto_id, paginate, randomnumber, send_email

# Create your views here.
@login_required
@role_required(['superadmin','director'])
def executive_info(request,pk):
    """
    Executive info
    :param request:
    :return: Executive info view
    """
    instance = Executive.objects.get(pk=pk,is_deleted=False)

    context = {
        'instance': instance,
        'page_name' : 'Executive Info',
        'page_title' : 'Executive Info',
        'is_executive_page' : True,
    }

    return render(request, 'admin_panel/pages/executive/info.html', context)

@login_required
@role_required(['superadmin','director'])
def executive_list(request):
    """
    Executive listings
    :param request:
    :return: Executive list view
    """
    instances = Executive.objects.filter(is_deleted=False).order_by("-date_added")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(investor_id__icontains=query) 
        )
        title = "Executive - %s" % query
        filter_data['q'] = query

    context = {
        'instances': instances,
        'page_name' : 'Executive',
        'page_title' : 'Executive',
        'filter_data' :filter_data,
        'is_executive_page' : True,
    }

    return render(request, 'admin_panel/pages/executive/list.html', context)

@login_required
@role_required(['superadmin','director'])
def create_executive(request):
    """
    create operation of Executive
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        # if instance go to edit
        form = ExecutiveForm(request.POST,files=request.FILES)
            
        if form.is_valid():
            try:
                with transaction.atomic():
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                        
                    user_data = User.objects.create_user(
                        username=email,
                        password=password,
                        is_active=True,
                    )
                    
                    group_names = ["executive",form.cleaned_data["department"].name]

                    for group_name in group_names:
                        if Group.objects.filter(name=group_name).exists():
                            group = Group.objects.get(name=group_name)
                        else:
                            group = Group.objects.create(name=group_name)
                        user_data.groups.add(group)
                    
                    auto_id = get_auto_id(Executive)
                    regid = "IEEIE" + str(auto_id).zfill(3)
                    
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
                        "message": "Executive created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('executive:executive_list')
                    }
                    
            except IntegrityError as e:
                # Handle database integrity error
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }

            except Exception as e:
                # Handle other exceptions
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
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
        
        form = ExecutiveForm()

        context = {
            'form': form,
            'page_name' : 'Create Executive',
            'page_title' : 'Create Executive',
            'url' : reverse('executive:create_executive'),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_executive_page' : True,
        }

        return render(request, 'admin_panel/pages/executive/create.html',context)
    
@login_required
@role_required(['superadmin','director'])
def edit_executive(request,pk):
    """
    edit operation of investor
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(Executive, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = ExecutiveEditForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update Executive
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Executive Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('executive:executive_list')
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
        
        form = ExecutiveEditForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Create Executive',
            'page_title' : 'Create Executive',
            'url' : reverse('executive:edit_executive', kwargs={'pk': pk}),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_executive_page' : True,
        }

        return render(request, 'admin_panel/pages/executive/create.html',context)

@login_required
@role_required(['superadmin','director'])
def delete_executive(request, pk):
    """
    Executive deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    instance = Executive.objects.get(pk=pk)
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
        "message": "Executive Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('executive:executive_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')