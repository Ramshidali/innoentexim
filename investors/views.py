#standerd
import io
import json
import datetime
#django
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.contrib.auth.models import User,Group
from django.db import transaction, IntegrityError
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
#rest framwework section
from rest_framework import status
from rest_framework.response import Response
# third party
from openpyxl import Workbook
#local
from . models import Investors
from profit.models import MyProfit
from main.decorators import role_required
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
        'is_investors_page': True,
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
            Q(investor_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(state__icontains=query) |
            Q(country__icontains=query)
        )
        title = "Investors - %s" % query
        filter_data['q'] = query

    context = {
        'instances': instances,
        'page_name' : 'Investors',
        'page_title' : 'Investors',
        'filter_data' :filter_data,
        'is_investors_page' : True,
    }

    return render(request, 'admin_panel/pages/investors/list.html', context)

@login_required
@role_required(['superadmin','director'])
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
            try:
                with transaction.atomic():
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
        
        form = InvestorsForm()

        context = {
            'form': form,
            'page_name' : 'Create Investors',
            'page_title' : 'Create Investors',
            'url' : reverse('investors:create_investor'),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_investors_page' : True,
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
            'is_investors_page' : True,
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


@login_required
@role_required(['superadmin','core_team','director','investor'])
def print_investors(request):
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
            Q(investor_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(state__icontains=query) |
            Q(country__icontains=query)
        )
        title = "Investors - %s" % query
        filter_data['q'] = query

    context = {
        'instances': instances,
        'page_name' : 'Investors',
        'page_title' : 'Investors',
        'filter_data' :filter_data,
        'is_investors_page' : True,
    }

    return render(request, 'admin_panel/pages/investors/print.html', context)

@login_required
@role_required(['superadmin','core_team','director','investor'])
def export_investors(request):
    filter_data = {}
    investor_pk = request.GET.get("investor_pk")

    investors = Investors.objects.filter(is_deleted=False)

    if investor_pk:
        investors = investors.filter(pk=investor_pk)
        
    date_range = request.GET.get('date_range')
    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        investors = investors.filter(date_of_birth__range=[start_date, end_date])
        filter_data['date_range'] = date_range
    
    query = request.GET.get("q")
    if query:
        investors = investors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) 
        )
        filter_data['q'] = query

    # Create a workbook and a worksheet
    wb = Workbook()
    ws = wb.active

    # Define column headers
    ws.append(['Investor ID','First Name','Last Name','Email','Phone','Date of Birth','Address','Investment Amount','Share Percentage','State','Country','Zip'])

    # Fetch and write data to Excel
    for investor in investors:
        ws.append([
            investor.investor_id,
            investor.first_name,
            investor.last_name,
            investor.email,
            investor.phone,
            investor.date_of_birth,
            investor.address,
            investor.investment_amount,
            investor.share_persentage,
            investor.state,
            investor.country,
            investor.zip
        ])

    # Prepare response
    output = io.BytesIO()
    wb.save(output)

    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=investors_data.xlsx'

    return response
