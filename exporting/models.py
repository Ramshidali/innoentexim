#django
import uuid
from django.db import models
#third party
#local
from main.models import BaseModel
from purchase.models import PurchaseItems, PurchaseStock

# Create your models here.
EXPORT_STATUS = (
    ('010', 'Pending'),
    ('015', 'Shipped'),
    ('020', 'Out of Delivery'),
    ('025', 'Delived'),
)


class ExportingCountry(BaseModel):
    country_name = models.CharField(max_length=200)
    cash_type = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'exporting_country_name'
        verbose_name = ('Exporting Country Name')
        verbose_name_plural = ('Exporting Country Name')
        
    def __str__(self):
        return f'{self.country_name}'
    
class CourierPartner(BaseModel):
    employee_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    services_offered = models.TextField(blank=True, null=True)
    tracking_url = models.CharField(max_length=100,blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'exporting_courier_partners'
        verbose_name = ('Exporting Courier Partners')
        verbose_name_plural = ('Exporting Courier Partners')
    
    def __str__(self):
        return self.name

class Exporting(BaseModel):
    exporting_id = models.CharField(max_length=200)
    date = models.DateField(default=None, null=True, blank=True)
    exporting_country = models.ForeignKey(ExportingCountry, on_delete=models.CASCADE)
    courier_partner = models.ForeignKey(CourierPartner, on_delete=models.CASCADE)
    is_editable = models.BooleanField(default=False)

    class Meta:
        db_table = 'exporting'
        verbose_name = ('Exporting')
        verbose_name_plural = ('Exporting')

    def __str__(self):
        return f'{self.exporting_id}'

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = self.date_added.date()
        super().save(*args, **kwargs)

    # def sub_total(self):
    #     total = 0
    #     # Calculate the sub-total for PurchasedItems
    #     items = self.exportitem_set.all()
    #     for item in items:
    #         total += item.amount
    #     # Calculate the sub-total for PurchaseMoreExpense
    #     # expenses = self.exportexpense_set.all()
    #     # for expense in expenses:
    #     #     total += expense.amount
    #     return total
    
    def total_qty(self):
        total = 0
        # Calculate the sub-total for PurchaseMaterials
        items = self.exportitem_set.all()
        for item in items:
            total += item.qty

        return total
    
    # def items_total_amount(self):
    #     total = 0
    #     # Calculate the sub-total for PurchaseMaterials
    #     items = self.exportitem_set.all()
    #     for item in items:
    #         total += item.amount

    #     return total
    
    def current_status(self):
        status = ""
        status = self.exportstatus_set.latest().get_status_display()
        
        return status

class ExportItem(BaseModel):
    qty = models.PositiveIntegerField()
    
    export = models.ForeignKey(Exporting, on_delete=models.CASCADE)
    purchasestock = models.ForeignKey(PurchaseStock, on_delete=models.CASCADE)

    class Meta:
        db_table = 'export_item'
        verbose_name = ('Export Material')
        verbose_name_plural = ('Export Materials')

    def __str__(self):
        return f'{self.qty} {self.amount}'
    
class ExportStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateTimeField(db_index=True, auto_now_add=True)
    status = models.CharField(max_length=200,choices=EXPORT_STATUS, default="010")
    caption = models.TextField()
    export = models.ForeignKey(Exporting, on_delete=models.CASCADE)
    creator = models.ForeignKey(
        "auth.User", blank=True, related_name="creator_%(class)s_objects", on_delete=models.CASCADE)

    class Meta:
        db_table = 'export_status'
        verbose_name = ('Export Status')
        verbose_name_plural = ('Export Status')
        get_latest_by = ('date_added')

    def __str__(self):
        return f'{self.status}'