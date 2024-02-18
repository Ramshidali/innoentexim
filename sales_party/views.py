#standerd
import json
import datetime
#django
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
#local
from . models import SalesParty
from . forms import SalesPartyForm
from main.decorators import role_required
from main.functions import encrypt_message, generate_form_errors, get_auto_id, has_group, paginate, randomnumber, send_email

# Create your views here.
@login_required
@role_required(['superadmin','core_team'])
def sales_party_info(request,pk):
    """
    Sales Party info
    :param request:
    :return: Sales Party info view
    """
    instance = SalesParty.objects.get(pk=pk,is_deleted=False)

    context = {
        'instance': instance,
        'page_name' : 'Sales Party',
        'page_title' : 'Sales Party',
        
        'is_sales': True,
        'is_sales_party_page': True,
    }

    return render(request, 'admin_panel/pages/sales_party/info.html', context)

@login_required
@role_required(['superadmin','core_team'])
def sales_party_list(request):
    """
    Sales Party listings
    :param request:
    :return: Sales Party list view
    """
    instances = SalesParty.objects.filter(is_deleted=False).order_by("-date_added")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(customer_id__icontains=query)
        )
        title = "SalesParty - %s" % query
        filter_data['q'] = query
    
    # if has_group(request.user,'core_team') :
    #     core_team = CoreTeam.objects.get(email=request.user)
    #     instances = instances.filter(branch__in=core_team.branch.all())

    context = {
        'instances': instances,
        'page_name' : 'Sales Party',
        'page_title' : 'Sales Party',
        'filter_data' :filter_data,
        
        'is_sales': True,
        'is_sales_party_page': True,
    }

    return render(request, 'admin_panel/pages/sales_party/list.html', context)

@login_required
@role_required(['superadmin','core_team'])
def create_sales_party(request):
    """
    create operation of Sales Party
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        form = SalesPartyForm(request.POST)
            
        if form.is_valid():
            
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            try:
                with transaction.atomic():
                
                    user_data = User.objects.create_user(
                        username=email,
                    )
                    
                    if Group.objects.filter(name="sales_party").exists():
                        group = Group.objects.get(name="sales_party")
                    else:
                        group = Group.objects.create(name="sales_party")

                    user_data.groups.add(group)
                    
                    auto_id = get_auto_id(SalesParty)
                    regid = "IEEISP" + str(auto_id).zfill(3)
                    
                    data = form.save(commit=False)
                    data.auto_id = auto_id
                    data.creator = request.user
                    data.date_updated = datetime.datetime.today()
                    data.updater = request.user
                    data.party_id = regid
                    data.user = user_data
                    data.save()
                    
                    response_data = {
                    "status": "true",
                    "title": "Successfully Created",
                    "message": "Sales Party created successfully.",
                    'redirect': 'true',
                    "redirect_url": reverse('sales_party:sales_party_list')
                    }
                
                    # base_url = request.scheme + "://" + request.get_host()
                    # # print(base_url)
                    # mail_html = render_to_string('admin_panel/pages/varification_mail/varification_mail_content.html', {'user_data': data, 'encrypt_id':encrypt_id,'base_url':base_url})
                    # if settings.SERVER :
                    #     mail_message = strip_tags(mail_html)
                    #     send_email("MRM user varification",form.cleaned_data['email'],mail_message,mail_html)
                    # else:
                    #     print(mail_html)
            except IntegrityError as e:
                
                if (SalesParty.objects.filter(phone=phone).exists() and SalesParty.objects.filter(email=email).exists()):
                    message = "This email id and phone number are already registered"
                     
                elif SalesParty.objects.filter(phone=phone).exists():
                    message = "This phone number already registered"
                
                elif SalesParty.objects.filter(email=email).exists():
                    message = "This email id already registered"
                    
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": message,
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
        
        form = SalesPartyForm()

        context = {
            'form': form,
            'page_name' : 'Create Sales Party',
            'page_title' : 'Create Sales Party',
            'url' : reverse('sales_party:create_sales_party'),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_sales': True,
            'is_sales_party_page': True,
        }

        return render(request, 'admin_panel/pages/sales_party/create.html',context)
    
@login_required
@role_required(['superadmin','core_team'])
def edit_sales_party(request,pk):
    """
    edit operation of sales_party
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(SalesParty, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = SalesPartyForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update SalesParty
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Sales Party Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('sales_party:sales_party_list')
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
        
        form = SalesPartyForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Edit Sales Party',
            'page_title' : 'Edit Sales Party',
            'url' : reverse('sales_party:edit_sales_party', kwargs={'pk': pk}),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_sales': True,
            'is_sales_party_page': True,
        }

        return render(request, 'admin_panel/pages/sales_party/create.html',context)

@login_required
@role_required(['superadmin','core_team'])
def delete_sales_party(request, pk):
    """
    SalesParty deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    instance = SalesParty.objects.get(pk=pk)
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
        "message": "Sales Party Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('sales_party:sales_party_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')