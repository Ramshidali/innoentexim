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
from . models import PurchaseParty
from . forms import PurchasePartyForm
from main.decorators import role_required
from main.functions import encrypt_message, generate_form_errors, get_auto_id, has_group, paginate, randomnumber, send_email

# Create your views here.
@login_required
@role_required(['superadmin','core_team'])
def purchase_party_info(request,pk):
    """
    Purchase Party info
    :param request:
    :return: Purchase Party info view
    """
    instance = PurchaseParty.objects.get(pk=pk,is_deleted=False)

    context = {
        'instance': instance,
        'page_name' : 'Purchase Party',
        'page_title' : 'Purchase Party',
        'is_purchase' : True,
        'is_purchase_party': True,
    }

    return render(request, 'admin_panel/pages/purchase_party/info.html', context)

@login_required
@role_required(['superadmin','core_team'])
def purchase_party_list(request):
    """
    Purchase Party listings
    :param request:
    :return: Purchase Party list view
    """
    instances = PurchaseParty.objects.filter(is_deleted=False).order_by("-date_added")
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(customer_id__icontains=query)
        )
        title = "PurchaseParty - %s" % query
        filter_data['q'] = query
    

    context = {
        'instances': instances,
        'page_name' : 'Purchase Party',
        'page_title' : 'Purchase Party',
        'filter_data' :filter_data,
        'is_purchase' : True,
        'is_purchase_party': True,
    }

    return render(request, 'admin_panel/pages/purchase_party/list.html', context)

@login_required
@role_required(['superadmin','core_team'])
def create_purchase_party(request):
    """
    create operation of Purchase Party
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        form = PurchasePartyForm(request.POST,files=request.FILES)
            
        if form.is_valid():
            
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            try:
                with transaction.atomic():
                
                    user_data = User.objects.create_user(
                        username=email,
                    )
                    
                    if Group.objects.filter(name="purchase_party").exists():
                        group = Group.objects.get(name="purchase_party")
                    else:
                        group = Group.objects.create(name="purchase_party")

                    user_data.groups.add(group)
                    
                    auto_id = get_auto_id(PurchaseParty)
                    regid = "IEEIPP" + str(auto_id).zfill(3)
                    
                    data = form.save(commit=False)
                    data.auto_id = auto_id
                    data.creator = request.user
                    data.date_updated = datetime.datetime.today()
                    data.updater = request.user
                    data.employee_id = regid
                    data.user = user_data
                    data.save()
                    
                    response_data = {
                    "status": "true",
                    "title": "Successfully Created",
                    "message": "Purchase Party created successfully.",
                    'redirect': 'true',
                    "redirect_url": reverse('purchase_party:purchase_party_list')
                    }
                
            except IntegrityError as e:
                    
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
        
        form = PurchasePartyForm()

        context = {
            'form': form,
            'page_name' : 'Create Purchase Party',
            'page_title' : 'Create Purchase Party',
            'url' : reverse('purchase_party:create_purchase_party'),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_purchase' : True,
            'is_purchase_party': True,
        }

        return render(request, 'admin_panel/pages/purchase_party/create.html',context)
    
@login_required
@role_required(['superadmin','core_team'])
def edit_purchase_party(request,pk):
    """
    edit operation of purchase_party
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(PurchaseParty, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = PurchasePartyForm(request.POST,files=request.FILES,instance=instance)
        
        if form.is_valid():
            #update PurchaseParty
            data = form.save(commit=False)
            data.date_updated = datetime.datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Purchase Party Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('purchase_party:purchase_party_list')
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
        
        form = PurchasePartyForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Edit Purchase Party',
            'page_title' : 'Edit Purchase Party',
            'url' : reverse('purchase_party:edit_purchase_party', kwargs={'pk': pk}),
            
            'is_need_datetime_picker': True,
            'is_need_forms': True,
            'is_purchase' : True,
            'is_purchase_party': True,
        }

        return render(request, 'admin_panel/pages/purchase_party/create.html',context)

@login_required
@role_required(['superadmin','core_team'])
def delete_purchase_party(request, pk):
    """
    PurchaseParty deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    instance = PurchaseParty.objects.get(pk=pk)
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
        "message": "Purchase Party Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('purchase_party:purchase_party_list'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')