import uuid
from datetime import datetime

from django.apps import apps
from django.db import models
from django.shortcuts import render
from django.db.models import Sum, Q

from main.models import BaseModel
from coreteam.models import CoreTeam
from investors.models import Investors
from executieves.models import Executive
from purchase_party.models import PurchaseParty

# Create your models here.
class PurchaseItems(BaseModel):
    name = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'purchase_items'
        verbose_name = ('Purchase Items')
        verbose_name_plural = ('Purchase Items')
    
    def __str__(self):
        return str(self.name)
    
    def get_user(self):
        if CoreTeam.objects.filter(user=self.creator,is_deleted=False).exists():
            instance = CoreTeam.objects.get(user=self.creator,is_deleted=False)
            user_name = f'{instance.first_name} {instance.last_name}'
        elif Investors.objects.filter(user=self.creator,is_deleted=False).exists():
            instance = Investors.objects.get(user=self.creator,is_deleted=False)
            user_name = f'{instance.first_name} {instance.last_name}'
        else:
          user_name = self.creator.username
            
        return user_name

class Purchase(BaseModel):
    purchase_id = models.CharField(max_length=100)
    date = models.DateField(default=None, null=True, blank=True)
    
    purchase_party = models.ForeignKey(PurchaseParty,on_delete=models.CASCADE)
    executive = models.ForeignKey(Executive,on_delete=models.CASCADE,null=True,blank=True)
    
    class Meta:
        db_table = 'purchase'
        verbose_name = ('Purchase')
        verbose_name_plural = ('Purchase')
    
    def __str__(self):
        return f'{self.purchase_id}'
    
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = self.date_added.date()
        super().save(*args, **kwargs)
    
    def sub_total(self):
        total = 0
        # Calculate the sub-total for PurchasedItems
        purchased_items = self.purchaseditems_set.all()
        for item in purchased_items:
            total += item.amount
        # Calculate the sub-total for PurchaseMoreExpense
        purchase_expenses = self.purchaseexpense_set.all()
        for expense in purchase_expenses:
            total += expense.amount
        return total
    
    def total_qty(self):
        total = 0
        # Calculate the sub-total for PurchaseMaterials
        purchased_items = self.purchaseditems_set.all()
        for item in purchased_items:
            total += item.qty

        return total
    
    def materials_total_amount(self):
        total = 0
        # Calculate the sub-total for PurchaseMaterials
        purchased_items = self.purchaseditems_set.all()
        for item in purchased_items:
            total += item.amount

        return total
    
    def materials_total_expence(self):
        total = 0
        purchase_expenses = self.purchaseexpense_set.all()
        for expense in purchase_expenses:
            total += expense.amount

        return total

class PurchasedItems(BaseModel):
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amount_per_kg = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    purchase_item = models.ForeignKey(PurchaseItems, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'purchased_items'
        verbose_name = ('Purchased Items')
        verbose_name_plural = ('Purchases Items')
    
    def __str__(self):
        return str(self.purchase_item.name)
    
    def total_expense(self):
        total_amount = 0
        for expense in self.purchasemoreexpense_set.all():
            total_amount += float(expense.amount)
        return total_amount
    
    
class PurchaseExpense(BaseModel):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase = models.ForeignKey(Purchase,on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'purchase_expences'
        verbose_name = ('Purchase Expences')
        verbose_name_plural = ('Purchase Expences')
    
    def __str__(self):
        return f'{self.title} {self.amount}'
    
    
class PurchaseStock(BaseModel):
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    
    purchase = models.ManyToManyField(Purchase)
    purchase_item = models.ForeignKey(PurchaseItems, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'purchase_stock'
        verbose_name = ('Purchase Stock')
        verbose_name_plural = ('Purchase Stock')
    
    def __str__(self):
        return f'{self.purchase_item.name}'