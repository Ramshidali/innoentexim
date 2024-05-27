from django.contrib import admin

from sales.models import *

# Register your models here.
admin.site.register(Sales)
admin.site.register(SalesItems)
admin.site.register(SalesExpenses)
admin.site.register(SalesStock)