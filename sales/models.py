from django.db import models
from django.core.validators import MinValueValidator

from main.models import BaseModel
from sales_party.models import SalesParty
from purchase.models import PurchaseItems
from exporting.models import Exporting, ExportingCountry

SALES_TYPES_CHOICES = (
    ('qty','QTY'),
    ('box','Box'),
)

# Create your models here.
class SalesStock(BaseModel):
    qty = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    export = models.ManyToManyField(Exporting)
    purchase_item = models.ForeignKey(PurchaseItems, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    country = models.ForeignKey(ExportingCountry, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
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
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    country = models.ForeignKey(ExportingCountry,on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    sales_staff = models.ForeignKey("auth.User",on_delete=models.CASCADE,related_name="sales_staff")
    sales_party = models.ForeignKey(SalesParty,on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'is_deleted': False})
    exporting = models.ManyToManyField(Exporting, limit_choices_to={'is_deleted': False})
    
    
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
    
    def sub_total_inr(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.amount_in_inr

        # Calculate the sub-total for SalesMoreExpense
        sales_expenses = SalesExpenses.objects.filter(sales=self)
        for expense in sales_expenses:
            total += expense.amount_in_inr

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
    
    def items_total_inr_amount(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.amount_in_inr
            
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
    
    def expenses_items_total_inr_amount(self):
        total = 0
        sales_expenses = SalesExpenses.objects.filter(sales=self)
        for expense in sales_expenses:
            total += expense.amount_in_inr
            
        return total
    
    def exchange_sub_total(self):
        total = 0
        # Calculate the sub-total for SalesItems
        sales_items = SalesItems.objects.filter(sales=self)
        for item in sales_items:
            total += item.amount_in_inr

        # Calculate the sub-total for SalesMoreExpense
        sales_expenses = SalesExpenses.objects.filter(sales=self)
        for expense in sales_expenses:
            total += expense.amount_in_inr
            
        return total

class SalesItems(BaseModel):
    no_boxes = models.PositiveIntegerField(default=0,null=True,blank=True)
    sale_type = models.CharField(max_length=10,choices=SALES_TYPES_CHOICES,default="qty")
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_in_inr = models.DecimalField(max_digits=10, decimal_places=2)
    
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    sales_stock = models.ForeignKey(SalesStock, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'sales_items'
        verbose_name = ('Sales Items')
        verbose_name_plural = ('Sales Items')
    
    def __str__(self):
        return f'{self.sale_type} {self.qty} {self.amount}'
    
    
class SalesExpenses(BaseModel):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_in_inr = models.DecimalField(max_digits=10, decimal_places=2)
    
    sales = models.ForeignKey(Sales,on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'sales_expences'
        verbose_name = ('Sales Expences')
        verbose_name_plural = ('Sales Expences')
    
    def __str__(self):
        return f'{self.title} {self.amount}'
    
class Damage(BaseModel):
    damage_id = models.CharField(max_length=200)
    date = models.DateField()
    
    country = models.ForeignKey(ExportingCountry,on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'damege'
        verbose_name = ('Damage')
        verbose_name_plural = ('Damage')
    
    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = self.date_added.date()
        super().save(*args, **kwargs)
    
    def total_qty(self):
        total = 0
        # Calculate the sub-total for DamageItems
        damage_items = DamageItems.objects.filter(damage=self)
        for item in damage_items:
            total += item.qty

        return total

class DamageItems(BaseModel):
    no_boxes = models.PositiveIntegerField(default=0,null=True,blank=True)
    weight_type = models.CharField(max_length=10,choices=SALES_TYPES_CHOICES,default="qty")
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    
    damage = models.ForeignKey(Damage, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    stock_item = models.ForeignKey(SalesStock, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'damage_items'
        verbose_name = ('Damage Items')
        verbose_name_plural = ('Damage Items')
    
    def __str__(self):
        return f'{self.weight_type} - {self.qty}'
    
class DamageStock(BaseModel):
    qty = models.DecimalField(default=0,max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    purchase_item = models.ForeignKey(PurchaseItems, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    country = models.ForeignKey(ExportingCountry, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'damage_stock'
        verbose_name = ('Damage Stock')
        verbose_name_plural = ('Damage Stock')
    
    def __str__(self):
        return f'{self.purchase_item.name} - {self.qty}'