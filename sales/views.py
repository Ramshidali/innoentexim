import io
import json
from datetime import timezone
import datetime
from datetime import datetime
import random
#django
from django.urls import reverse
from django.db.models import Q, Sum
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User,Group
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
from profit.views import calculate_profit
# rest framework
from rest_framework import status
# local
from profit.models import *
from main.decorators import role_required
from sales.serializers import SalesStockSerializer
from sales.forms import SalesExpenseForm, SalesForm, SalesItemsForm
from sales.models import Sales, SalesExpenses, SalesItems, SalesStock
from main.functions import generate_form_errors, get_auto_id, get_current_role, has_group

# Create your views here.
def get_sales_product_items(request):
    country_id = request.GET.get('country_id')
    product_items = SalesStock.objects.filter(qty__gt=0,country_id=country_id)
    data = [{'id': item.id, 'name': item.purchase_item.name} for item in product_items]

    return JsonResponse(data, safe=False)

def sales_item_qty(request):
    item_pk = request.GET.get("item_pk")
    country_pk = request.GET.get("country")
    
    if (instances:=SalesStock.objects.filter(pk=item_pk,country=country_pk,is_deleted=False)).exists():
        qty = instances.first().qty
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": "true",
            "qty": str(qty),
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": "item not found",
        }

    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")

@login_required
@role_required(['superadmin','core_team','director'])
def sales_stock(request):
    """
    Sales Stock
    :param request:
    :return: Sales Stock List
    """
    filter_data = {}
    instances = SalesStock.objects.filter(is_deleted=False)
    
    if request.GET.get("country"):
        instances = instances.filter(country__pk=request.GET.get("country"))
        filter_data['country'] = request.GET.get("country")
        
    context = {
        'instances': instances,
        'page_name' : 'Sales Stock',
        'page_title' : 'Sales Stock',
        'filter_data': filter_data,
        
        'is_sales' : True,
        'is_sales_stock_page': True,
    }

    return render(request, 'admin_panel/pages/sales/stock/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def sales_info(request,pk):
    """
    Sale Info
    :param request:
    :return: Sale Info single view
    """
    
    instance = Sales.objects.get(pk=pk)

    context = {
        'instance': instance,
        'page_name' : 'Sale Info',
        'page_title' : 'Sale Info',
    }

    return render(request, 'admin_panel/pages/sales/sales/info.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def sales_list(request):
    """
    Sales List
    :param request:
    :return: Sales List list view
    """
    filter_data = {}
    
    instances = Sales.objects.filter(is_deleted=False).order_by("-date_added")
         
    if request.GET.get('date_range'):
        start_date_str, end_date_str = request.GET.get('date_range').split(' - ')
        start_date = datetime.datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date__range=[start_date, end_date])
        
        filter_data['date_range'] = request.GET.get('date_range')
    
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(sales_id__icontains=query) 
        )
        title = "Sales List - %s" % query
        filter_data['q'] = query
    
    # branch = ""
    # if request.GET.get("branch"):
    #     branch = request.GET.get("branch")
    #     instances = instances.filter(branch__pk=branch)
        
    if request.GET.get("party"):
        party = request.GET.get("party")
        instances = instances.filter(sales_party__pk=party)
        filter_data['party'] = request.GET.get("party")
        
    # print(branch)
    context = {
        'instances': instances,
        'page_name' : 'Sales List',
        'page_title' : 'Sales List',
        'filter_data' :filter_data,
        'is_sales' : True,
        'is_sales_page': True,
    }

    return render(request, 'admin_panel/pages/sales/sales/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def create_sales(request):
    ItemsFormset = formset_factory(SalesItemsForm, extra=2)
    ExpensesFormset = formset_factory(SalesExpenseForm, extra=2)
    
    message = ''
    if request.method == 'POST':
        form = SalesForm(request.POST)
        sales_items_formset = ItemsFormset(request.POST,prefix='sales_items_formset', form_kwargs={'empty_permitted': False})
        sales_expense_formset = ExpensesFormset(request.POST,prefix='sales_expense_formset', form_kwargs={'empty_permitted': False})
        
        if form.is_valid() and sales_items_formset.is_valid() and sales_expense_formset.is_valid():
            
            date_part = datetime.now().strftime('%Y%m%d')
            random_part = str(random.randint(1000, 9999))
            invoice_number = f'IEEIP-{date_part}-{random_part}'
            auto_id = get_auto_id(Sales)
            sales_id = "IEEIS" + str(auto_id).zfill(3)    
            
            try:
                with transaction.atomic():
                    inr_exchange_rate = ExchangeRate.objects.filter(country=form.cleaned_data['country'],is_active=True).latest('-date_added').rate_to_inr
                            
                    if form.is_valid():
                        sales_data = form.save(commit=False)
                        sales_data.auto_id = get_auto_id(Sales)
                        sales_data.creator = request.user
                        sales_data.sales_staff = request.user
                        sales_data.sales_id = sales_id
                        sales_data.invoice_no = invoice_number
                        sales_data.exchange_rate = inr_exchange_rate
                        sales_data.save()
                    
                    for form in sales_items_formset:
                        item_data = form.save(commit=False)
                        item_data.auto_id = get_auto_id(SalesItems)
                        item_data.creator = request.user
                        item_data.sales = sales_data
                        item_data.amount_in_inr = form.cleaned_data['amount'] * inr_exchange_rate
                        item_data.save()
                        
                        if (stock:=SalesStock.objects.filter(country=sales_data.country,purchase_item=item_data.sales_stock.purchase_item)).exists():
                            stock = stock.first()
                            stock.qty -= item_data.qty
                            stock.save()
                        else:
                            stock = SalesStock.objects.create(
                                auto_id = get_auto_id(SalesStock),
                                creator = request.user,
                                date_updated = datetime.datetime.today(),
                                updater = request.user,
                                country = sales_data.country,
                                purchase_item = item_data.sales_stock.purchase_item,
                                qty = item_data.qty,
                            )
                    
                    for form in sales_expense_formset:
                        expense_data = form.save(commit=False)
                        expense_data.auto_id = get_auto_id(SalesExpenses)
                        expense_data.creator = request.user
                        expense_data.sales = sales_data
                        expense_data.amount_in_inr = form.cleaned_data['amount'] * inr_exchange_rate
                        expense_data.save()
                    
                    calculate_profit(sales_data.date)
                    
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Sales created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('sales:sales_list')
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
            message = generate_form_errors(form,formset=False)
            message += generate_form_errors(sales_items_formset,formset=True)
            message += generate_form_errors(sales_expense_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        form = SalesForm()
        sales_items_formset = ItemsFormset(prefix='sales_items_formset')
        sales_expense_formset = ExpensesFormset(prefix='sales_expense_formset')
        
        context = {
            'form': form,
            'sales_items_formset': sales_items_formset,
            'sales_expense_formset': sales_expense_formset,
            
            'page_title': 'Create Sales',
            'url': reverse('sales:create_sales'),
            'is_sales' : True,
            'is_sales_page': True,
            'is_need_datetime_picker': True,
        }
        
        return render(request,'admin_panel/pages/sales/sales/create.html',context)

@login_required
@role_required(['superadmin','core_team','director'])
def edit_sales(request,pk):
    """
    edit operation of sales
    :param request:
    :param pk:
    :return:
    """
    sales_instance = get_object_or_404(Sales, pk=pk)
    salesd_items = SalesItems.objects.filter(sales=sales_instance)
    expences = SalesExpenses.objects.filter(sales=sales_instance)
    
    if SalesItems.objects.filter(sales=sales_instance).exists():
        i_extra = 0
    else:
        i_extra = 1 
        
    if SalesExpenses.objects.filter(sales=sales_instance).exists():
        e_extra = 0
    else:
        e_extra = 1 

    ItemsFormset = inlineformset_factory(
        Sales,
        SalesItems,
        extra=i_extra,
        form=SalesItemsForm,
    )
    
    ExpencesFormset = inlineformset_factory(
        Sales,
        SalesExpenses,
        extra=e_extra,
        form=SalesExpenseForm,
    )
        
    message = ''
    
    if request.method == 'POST':
        form = SalesForm(request.POST,instance=sales_instance)
        sales_items_formset = ItemsFormset(request.POST,request.FILES,
                                            instance=sales_instance,
                                            prefix='sales_items_formset',
                                            form_kwargs={'empty_permitted': False})            
        sales_expense_formset = ExpencesFormset(request.POST,
                                            instance=sales_instance, 
                                            prefix='sales_expense_formset', 
                                            form_kwargs={'empty_permitted': False})            
        
        if form.is_valid() and  sales_items_formset.is_valid() and sales_expense_formset.is_valid():
            #create
            data = form.save(commit=False)
            data.date_updated = datetime.today()
            data.updater = request.user
            data.date = request.POST.get('date')
            data.save()
            
            inr_exchange_rate = ExchangeRate.objects.filter(country=data.country,is_active=True).latest('-date_added').rate_to_inr
            
            for form in sales_items_formset:
                if form not in sales_items_formset.deleted_forms:
                    i_data = form.save(commit=False)
                    i_data.amount_in_inr = form.cleaned_data['amount'] * inr_exchange_rate
                    if not i_data.auto_id :
                        i_data.sales = sales_instance
                        i_data.auto_id = get_auto_id(SalesItems)
                        i_data.creator = request.user
                    i_data.save()

            for f in sales_items_formset.deleted_forms:
                f.instance.delete()
                
            for form in sales_expense_formset:
                if form not in sales_expense_formset.deleted_forms:
                    e_data = form.save(commit=False)
                    if not e_data.auto_id :
                        e_data.auto_id = get_auto_id(SalesExpenses)
                        e_data.creator = request.user
                        e_data.sales = sales_instance
                    e_data.save()

            for f in sales_expense_formset.deleted_forms:
                f.instance.delete()
                
            calculate_profit(data.date)
                
            response_data = {
                "status": "true",
                "title": "Successfully Updated",
                "message": "Sales Updated Successfully.",
                'redirect': 'true',
                "redirect_url": reverse('sales:sales_list'),
                "return" : True,
            }
    
        else:
            message = generate_form_errors(form,formset=False)
            message += generate_form_errors(sales_items_formset,formset=True)
            message += generate_form_errors(sales_expense_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                        
    else:
        form = SalesForm(instance=sales_instance)
        sales_items_formset = ItemsFormset(queryset=salesd_items,
                                            prefix='sales_items_formset',
                                            instance=sales_instance)
        sales_expense_formset = ExpencesFormset(queryset=expences, 
                                                    prefix='sales_expense_formset', 
                                                    instance=sales_instance)
        

        context = {
            'form': form,
            'sales_items_formset': sales_items_formset,
            'sales_expense_formset': sales_expense_formset,
            
            'message': message,
            'page_name' : 'edit sales',
            'is_sales' : True,
            'is_sales_page': True,        
        }

        return render(request, 'admin_panel/pages/sales/sales/create.html', context)
    
@login_required
@role_required(['superadmin','core_team','director'])
def delete_sales(request, pk):
    """
    sales deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    # sales = Sales.objects.get(pk=pk)
    # if sales.sales_manager_is_varified == True :
    #     if not Sales.objects.filter(sales=sales,is_deleted=False).exists():
    #         if (materials:=SalesMaterials.objects.filter(sales=sales,is_deleted=False)).exists():
    #             for material in materials:
    #                 sales_items = material.sales_item
    #                 branch = material.sales.branch.pk
    #                 qty = material.qty
                    
    #                 if (stocks:=Stock.objects.filter(sales=sales,sales_item__pk=sales_items.pk,branch__pk=branch,is_deleted=False)).exists():
    #                     for stock in stocks:
    #                         stock.qty -= qty
    #                         stock.save()
                        
    #                         stock.sales.remove(sales)
                            
    #             materials.update(is_deleted=True)
                            
    #         sales.is_deleted=True
    #         sales.save()

    #         response_data = {
    #             "status": "true",
    #             "title": "Successfully Deleted",
    #             "message": "Sales Successfully Deleted.",
    #             "redirect": "true",
    #             "redirect_url": reverse('sales:sales_list'),
    #         }
    #     else:
    #         sales_queryset = Sales.objects.filter(sales=sales)
    #         sales_invoice_numbers = [sales.invoice_no for sales in sales_queryset]
    #         invoice_numbers_text = ", ".join(sales_invoice_numbers)
    #         message = f"This sales has already included the sale of some items. Sales Invoice Numbers: {invoice_numbers_text}"
            
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": message,
    #         }
    # else:
    #     sales.is_deleted=True
    #     sales.save()
        
    #     SalesMaterials.objects.filter(sales=sales).update(is_deleted=True)
    #     SalesMoreExpense.objects.filter(sales=sales).update(is_deleted=True)
        
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Sale Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('sales:sales_list'),
    }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')