from django.contrib import admin

from exporting.models import *

# Register your models here.
class ExportStatusAdmin(admin.ModelAdmin):
    list_display = [
        'date_added',
        'status',
        'caption',
        'creator',
        'export',
        ]
    def export(self, obj): 
        return obj.export.exporting_id
    
admin.site.register(ExportStatus,ExportStatusAdmin)
admin.site.register(CourierPartner)
admin.site.register(Exporting)

class ExportingCountryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'date_added',
        'country_name',
        'cash_type',
        ]
admin.site.register(ExportingCountry,ExportingCountryAdmin)