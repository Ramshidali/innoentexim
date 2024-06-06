from django.contrib import admin

from other_expences.models import ExpenceTypes, OtherExpences


# Register your models here.
admin.site.register(ExpenceTypes)
admin.site.register(OtherExpences)