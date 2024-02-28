import uuid
from datetime import date

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from sales.models import *
from purchase.models import *
from exporting.models import *
from main.models import BaseModel

class ExchangeRate(BaseModel):
    country = models.ForeignKey(ExportingCountry, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3)  # Currency code (e.g., USD, EUR)
    rate_to_inr = models.DecimalField(max_digits=10, decimal_places=6)  # Exchange rate to INR
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'exchange_rates'
        verbose_name = ('Exchange Rate')
        verbose_name_plural = ('Exchange Rates')
        
    def __str__(self):
        return f'{self.currency} to INR: {self.rate_to_inr}'

class DialyProfit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateTimeField(db_index=True, auto_now_add=True)
    purchase = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    purchase_expenses = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    sales = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    sales_expenses = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_expenses = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    profit = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'daily_profit'
        verbose_name = 'Daily Profit'
        verbose_name_plural = 'Daily Profits'

    def __str__(self):
        return f'Daily Profit {self.date_added}'