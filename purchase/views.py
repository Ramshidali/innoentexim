import io
import json
import datetime
from datetime import datetime
#django
from django.urls import reverse
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
#local
from executieves.models import Executive
from main.decorators import role_required
from main.functions import generate_form_errors, get_auto_id, get_current_role, has_group
from profit.views import calculate_profit
from purchase.models import Purchase, PurchaseExpense, PurchaseItems, PurchaseStock, PurchasedItems
from purchase.forms import PurchaseExpenseForm, PurchaseForm, PurchaseItemForm, PurchasedItemsForm

# Create your views here.
@login_required
@role_required(['superadmin','core_team','director'])
def purchase_items(request):
    """
    Purchase Items
    :param request:
    :return: Purchase Items List
    """
    instances = PurchaseItems.objects.filter(is_deleted=False)
    
    context = {
        'instances': instances,
        'page_name' : 'Purchase Items',
        'page_title' : 'Purchase Items',
        'is_purchase' : True,
        'is_purchase_items_page': True,
    }

    return render(request, 'admin_panel/pages/purchase/purchase_items/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def create_purchase_items(request):
    PurchaseItemsFormset = formset_factory(PurchaseItemForm, extra=2)
    
    message = ''
    if request.method == 'POST':
        purchase_items_formset = PurchaseItemsFormset(request.POST,prefix='purchase_items_formset', form_kwargs={'empty_permitted': False})
        
        if purchase_items_formset.is_valid() :
            for form in purchase_items_formset:
                data = form.save(commit=False)
                data.auto_id = get_auto_id(PurchaseItems)
                data.creator = request.user
                data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Product Item created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('purchase:purchase_items')
            }
    
        else:
            message = generate_form_errors(purchase_items_formset, formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        purchase_items_formset = PurchaseItemsFormset(prefix='purchase_items_formset')
        
        context = {
            'purchase_items_formset': purchase_items_formset,
            
            'page_title': 'Create Purchase Items',
            'url': reverse('purchase:create_purchase_items'),
            'is_purchase' : True,
            'is_purchase_items_page': True,
        }
        
        return render(request,'admin_panel/pages/purchase/purchase_items/create.html',context)
    
@login_required
@role_required(['superadmin','core_team','director'])
def edit_purchase_item(request,pk):
    """
    edit operation of purchase item
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(PurchaseItems, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST,instance=instance)
        
        if form.is_valid():
            
            data = form.save(commit=False)
            data.date_updated = datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Purchase Item Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('purchase:purchase_items')
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
        
        form = PurchaseItemForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Edit Purchase Items',
            'page_title' : 'Edit Purchase Items',
            'url' : reverse('purchase:create_purchase_items'),
            'is_purchase' : True,
            'is_purchase_items_page': True,  
        }

        return render(request, 'admin_panel/pages/purchase/purchase_items/edit.html',context)

@login_required
@role_required(['superadmin','core_team','director'])
def delete_purchase_items(request, pk):
    """
    purchase items deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    invoice_numbers_text = ""
    # data = PurchaseItems.objects.get(pk=pk)
    # if not SalesMaterials.objects.filter(purchase_item=data, is_deleted=False).exists():
        
    #     data.is_deleted=True
    #     data.save()
    
    #     if (instances:=PurchaseMaterials.objects.filter(purchase_item=data)).exists():
    #         instances.update(is_deleted=True)
            
    #     if (stocks:=Stock.objects.filter(purchase_item=data)).exists():
    #         stocks.update(is_deleted=True)

    #     response_data = {
    #         "status": "true",
    #         "title": "Successfully Deleted",
    #         "message": "Purchase Item Successfully Deleted.",
    #         "redirect": "true",
    #         "redirect_url": reverse('purchase:purchase_items'),
    #     }
    # else:
    #     sales_material_queryset = SalesMaterials.objects.filter(purchase_item=data)
    #     sales_invoice_numbers = [sales_material.sales.invoice_no for sales_material in sales_material_queryset]
    #     unique_invoice_numbers = list(set(sales_invoice_numbers))
    #     invoice_numbers_text = ", ".join(unique_invoice_numbers)

    message = f"This purchase item has already included the sale of some items. Sales Invoice Numbers: {invoice_numbers_text}"
    
    response_data = {
        "status": "false",
        "title": "Failed",
        "message": message,
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')

@login_required
@role_required(['superadmin','core_team','director'])
def purchase(request,pk):
    """
    Purchase
    :param request:
    :return: Purchase Report single view
    """
    instance = Purchase.objects.get(pk=pk,is_deleted=False)
    
    context = {
        'instance': instance,
        'page_name' : 'Purchase Report',
        'page_title' : 'Purchase Report',
        'purchase_page': True,
    }

    return render(request, 'admin_panel/pages/purchase/purchases/info.html', context)

# @login_required
# @role_required(['superadmin','core_team','director'])
# def print_purchase(request,pk):
#     """
#     Print Purchase
#     :param request:
#     :return: Purchase Print
#     """
#     instance = Purchase.objects.get(pk=pk,is_deleted=False)
    
#     context = {
#         'instance': instance,
#         'page_name' : 'Purchase Report',
#         'page_title' : 'Purchase Report',
#     }

#     return render(request, 'admin_panel/pages/purchase/print_purchase.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def purchase_reports(request):
    """
    Purchase Report
    :param request:
    :return: Purchase Report list view
    """
    
    instances = Purchase.objects.filter(is_deleted=False).order_by("-date_added")
         
    date_range = ""
    date_range = request.GET.get('date_range')
    # print(date_range)

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date__range=[start_date, end_date])
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(purchase_id__icontains=query) 
        )
        title = "Purchase Report - %s" % query
        filter_data['q'] = query
    
    
    context = {
        'instances': instances,
        'page_name' : 'Purchase Report',
        'page_title' : 'Purchase Report',
        'filter_data' :filter_data,
        'date_range': date_range,
        
        'is_purchase' : True,
        'is_purchase_page': True,
        'is_need_datetime_picker': True,
    }

    return render(request, 'admin_panel/pages/purchase/purchases/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def create_purchase(request):
    ItemsFormset = formset_factory(PurchasedItemsForm, extra=2)
    PurchaseExpensesFormset = formset_factory(PurchaseExpenseForm, extra=2)
    
    message = ''
    if request.method == 'POST':
        purchase_form = PurchaseForm(request.POST)
        purchase_items_formset = ItemsFormset(request.POST,prefix='purchase_items_formset', form_kwargs={'empty_permitted': False})
        purchase_expense_formset = PurchaseExpensesFormset(request.POST,prefix='purchase_expense_formset', form_kwargs={'empty_permitted': False})
        
        if purchase_form.is_valid() and purchase_items_formset.is_valid() and purchase_expense_formset.is_valid():
            
            # Generate a unique invoice number based on current date and a random number
            # date_part = timezone.now().strftime('%Y%m%d')
            # random_part = str(random.randint(1000, 9999))
            # invoice_number = f'IEEIP-{date_part}-{random_part}'
            executive = None
            if not request.user.is_superuser:
                executive = Executive.objects.get(user=request.user,is_deleted=False)
            
            auto_id = get_auto_id(Purchase)
            purchase_id = "IEEIP" + str(auto_id).zfill(3)    
            
            try:
                with transaction.atomic():
                    
                    if purchase_form.is_valid():
                        purchase_data = purchase_form.save(commit=False)
                        purchase_data.auto_id = get_auto_id(Purchase)
                        purchase_data.creator = request.user
                        purchase_data.executive = executive
                        purchase_data.purchase_id = purchase_id
                        purchase_data.save()
                    
                    for form in purchase_items_formset:
                        item_data = form.save(commit=False)
                        item_data.auto_id = get_auto_id(PurchasedItems)
                        item_data.creator = request.user
                        item_data.purchase = purchase_data
                        item_data.save()
                        
                        if (update_purchase_stock:=PurchaseStock.objects.filter(purchase_item=item_data.purchase_item,is_deleted=False)).exists():
                            stock = PurchaseStock.objects.get(purchase_item=item_data.purchase_item,is_deleted=False)
                            stock.qty += item_data.qty
                            if not update_purchase_stock.filter(purchase=purchase_data).exists():
                                stock.purchase.add(purchase_data)
                            stock.save()
                        else:
                            purchase_item = PurchaseItems.objects.get(pk=item_data.purchase_item.pk)
                            stock_item = PurchaseStock.objects.create(
                                auto_id = get_auto_id(PurchaseStock),
                                creator = request.user,
                                purchase_item = purchase_item,
                                qty = item_data.qty,
                            )
                            stock_item.purchase.add(purchase_data)
                            stock_item.save()
                    
                    for form in purchase_expense_formset:
                        expense_data = form.save(commit=False)
                        expense_data.auto_id = get_auto_id(PurchaseExpense)
                        expense_data.creator = request.user
                        expense_data.purchase = purchase_data
                        expense_data.save()
                        
                    calculate_profit(purchase_data.date)
                        
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Product created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('purchase:purchase_reports')
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
            message = generate_form_errors(purchase_form,formset=False)
            message += generate_form_errors(purchase_items_formset,formset=True)
            message += generate_form_errors(purchase_expense_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        purchase_form = PurchaseForm()
        purchase_items_formset = ItemsFormset(prefix='purchase_items_formset')
        purchase_expense_formset = PurchaseExpensesFormset(prefix='purchase_expense_formset')
        
        context = {
            'purchase_form': purchase_form,
            'purchase_items_formset': purchase_items_formset,
            'purchase_expense_formset': purchase_expense_formset,
            
            'page_title': 'Create Purchase',
            'url': reverse('purchase:create_purchase'),
            'is_purchase' : True,
            'is_purchase_page': True,
            'is_need_datetime_picker': True,
        }
        
        return render(request,'admin_panel/pages/purchase/purchases/create.html',context)

@login_required
@role_required(['superadmin','core_team','director'])
def edit_purchase(request,pk):
    """
    edit operation of purchase
    :param request:
    :param pk:
    :return:
    """
    purchase_instance = get_object_or_404(Purchase, pk=pk)
    purchased_items = PurchasedItems.objects.filter(purchase=purchase_instance)
    expences = PurchaseExpense.objects.filter(purchase=purchase_instance)
    
    if PurchasedItems.objects.filter(purchase=purchase_instance).exists():
        i_extra = 0
    else:
        i_extra = 1 
        
    if PurchaseExpense.objects.filter(purchase=purchase_instance).exists():
        e_extra = 0
    else:
        e_extra = 1 

    ItemsFormset = inlineformset_factory(
        Purchase,
        PurchasedItems,
        extra=i_extra,
        form=PurchasedItemsForm,
    )
    
    ExpencesFormset = inlineformset_factory(
        Purchase,
        PurchaseExpense,
        extra=e_extra,
        form=PurchaseExpenseForm,
    )
        
    message = ''
    
    if request.method == 'POST':
        purchase_form = PurchaseForm(request.POST,instance=purchase_instance)
        purchase_items_formset = ItemsFormset(request.POST,request.FILES,
                                            instance=purchase_instance,
                                            prefix='purchase_items_formset',
                                            form_kwargs={'empty_permitted': False})            
        purchase_expense_formset = ExpencesFormset(request.POST,
                                            instance=purchase_instance, 
                                            prefix='purchase_expense_formset', 
                                            form_kwargs={'empty_permitted': False})            
        
        if purchase_form.is_valid() and  purchase_items_formset.is_valid() and purchase_expense_formset.is_valid():
            #create
            data = purchase_form.save(commit=False)
            data.date_updated = datetime.today()
            data.updater = request.user
            data.date = request.POST.get('date')
            data.save()
            
            for form in purchase_items_formset:
                if form not in purchase_items_formset.deleted_forms:
                    i_data = form.save(commit=False)
                    if not i_data.auto_id :
                        i_data.purchase = purchase_instance
                        i_data.auto_id = get_auto_id(PurchasedItems)
                        i_data.creator = request.user
                    i_data.save()

            for f in purchase_items_formset.deleted_forms:
                f.instance.delete()
                
            for form in purchase_expense_formset:
                if form not in purchase_expense_formset.deleted_forms:
                    e_data = form.save(commit=False)
                    if not e_data.auto_id :
                        e_data.auto_id = get_auto_id(PurchaseExpense)
                        e_data.creator = request.user
                        e_data.purchase = purchase_instance
                    e_data.save()

            for f in purchase_expense_formset.deleted_forms:
                f.instance.delete()
                
            calculate_profit(data.date)
                
            response_data = {
                "status": "true",
                "title": "Successfully Updated",
                "message": "Purchase Updated Successfully.",
                'redirect': 'true',
                "redirect_url": reverse('purchase:purchase_reports'),
                "return" : True,
            }
    
        else:
            message = generate_form_errors(purchase_form,formset=False)
            message += generate_form_errors(purchase_items_formset,formset=True)
            message += generate_form_errors(purchase_expense_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                        
    else:
        purchase_form = PurchaseForm(instance=purchase_instance)
        purchase_items_formset = ItemsFormset(queryset=purchased_items,
                                            prefix='purchase_items_formset',
                                            instance=purchase_instance)
        purchase_expense_formset = ExpencesFormset(queryset=expences, 
                                                    prefix='purchase_expense_formset', 
                                                    instance=purchase_instance)
        

        context = {
            'purchase_form': purchase_form,
            'purchase_items_formset': purchase_items_formset,
            'purchase_expense_formset': purchase_expense_formset,
            
            'message': message,
            'page_name' : 'edit purchase',
            'is_purchase' : True,
            'is_purchase_page': True,        
        }

        return render(request, 'admin_panel/pages/purchase/purchases/create.html', context)
    
@login_required
@role_required(['superadmin','core_team','director'])
def delete_purchase(request, pk):
    """
    purchase deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    # purchase = Purchase.objects.get(pk=pk)
    # if purchase.purchase_manager_is_varified == True :
    #     if not Sales.objects.filter(purchase=purchase,is_deleted=False).exists():
    #         if (materials:=PurchaseMaterials.objects.filter(purchase=purchase,is_deleted=False)).exists():
    #             for material in materials:
    #                 purchase_items = material.purchase_item
    #                 branch = material.purchase.branch.pk
    #                 qty = material.qty
                    
    #                 if (stocks:=Stock.objects.filter(purchase=purchase,purchase_item__pk=purchase_items.pk,branch__pk=branch,is_deleted=False)).exists():
    #                     for stock in stocks:
    #                         stock.qty -= qty
    #                         stock.save()
                        
    #                         stock.purchase.remove(purchase)
                            
    #             materials.update(is_deleted=True)
                            
    #         purchase.is_deleted=True
    #         purchase.save()

    #         response_data = {
    #             "status": "true",
    #             "title": "Successfully Deleted",
    #             "message": "Purchase Successfully Deleted.",
    #             "redirect": "true",
    #             "redirect_url": reverse('purchase:purchase_reports'),
    #         }
    #     else:
    #         sales_queryset = Sales.objects.filter(purchase=purchase)
    #         sales_invoice_numbers = [sales.invoice_no for sales in sales_queryset]
    #         invoice_numbers_text = ", ".join(sales_invoice_numbers)
    #         message = f"This purchase has already included the sale of some items. Sales Invoice Numbers: {invoice_numbers_text}"
            
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": message,
    #         }
    # else:
    #     purchase.is_deleted=True
    #     purchase.save()
        
    #     PurchaseMaterials.objects.filter(purchase=purchase).update(is_deleted=True)
    #     PurchaseMoreExpense.objects.filter(purchase=purchase).update(is_deleted=True)
        
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Purchase Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('purchase:purchase_reports'),
    }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
@role_required(['superadmin','core_team','director'])
def purchase_stock(request):
    """
    Purchase Stocks
    :param request:
    :return: Purchase Stocks List
    """
    instances = PurchaseStock.objects.filter(is_deleted=False)
    
    context = {
        'instances': instances,
        'page_name' : 'Purchase Stocks',
        'page_title' : 'Purchase Stocks',
        'is_purchase' : True,
        'is_purchase_stock_page': True,
    }

    return render(request, 'admin_panel/pages/purchase/purchase_stock/list.html', context)