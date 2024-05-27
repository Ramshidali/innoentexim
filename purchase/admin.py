from django.contrib import admin

from purchase.models import *

# Register your models here.
admin.site.register(PurchaseItems)
admin.site.register(Purchase)
admin.site.register(PurchaseExpense)
admin.site.register(PurchaseStock)