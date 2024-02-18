from django.db import models
from exporting.models import Exporting, ExportingCountry

from main.models import BaseModel
from purchase.models import PurchaseItems
from sales_party.models import SalesParty

# Create your models here.
class SalesStock(BaseModel):
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    
    export = models.ManyToManyField(Exporting)
    purchase_item = models.ForeignKey(PurchaseItems, on_delete=models.CASCADE)
    country = models.ForeignKey(ExportingCountry, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'sales_stock'
        verbose_name = ('Sales Stock')
        verbose_name_plural = ('Sales Stock')
    
    def __str__(self):
        return f'{self.purchase_item.name}'
    
class Sales(BaseModel):
    invoice_no = models.CharField(max_length=200)
    sales_id = models.CharField(max_length=100)
    date = models.DateField(default=None, null=True, blank=True)
    
    country = models.ForeignKey(ExportingCountry,on_delete=models.CASCADE)
    sales_staff = models.ForeignKey("auth.User",on_delete=models.CASCADE,related_name="sales_staff")
    sales_party = models.ForeignKey(SalesParty,on_delete=models.CASCADE, null=True, blank=True)
    exporting = models.ManyToManyField(Exporting)
    
    
    class Meta:
        db_table = 'sales'
        verbose_name = ('Sales')
        verbose_name_plural = ('Sales')
    
    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = self.date_added.date()
        super().save(*args, **kwargs)
    
    def sub_total(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.amount

        # Calculate the sub-total for SalesMoreExpense
        sales_expenses = SalesExpenses.objects.filter(sales=self)
        for expense in sales_expenses:
            total += expense.amount

        return total
    
    def total_qty(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.qty

        return total
    
    def items_total_amount(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.amount
            
        return total
    
    def items_per_kg_amount(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.per_kg_amount
            
        return total    
    
    def items_total_expence(self):
        total = 0
        sales_expenses = SalesExpenses.objects.filter(sales=self)
        for expense in sales_expenses:
            total += expense.amount

        return total
    
class SalesItems(BaseModel):
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE)
    sales_stock = models.ForeignKey(SalesStock, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'sales_items'
        verbose_name = ('Sales Items')
        verbose_name_plural = ('Sales Items')
    
    def __str__(self):
        return f'{self.qty} {self.amount}'
    
class SalesExpenses(BaseModel):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    sales = models.ForeignKey(Sales,on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'sales_expences'
        verbose_name = ('Sales Expences')
        verbose_name_plural = ('Sales Expences')
    
    def __str__(self):
        return f'{self.title} {self.amount}'