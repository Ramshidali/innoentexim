import uuid
from datetime import date

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User

from sales.models import *
from purchase.models import *
from exporting.models import *
from main.models import BaseModel

class ExchangeRate(BaseModel):
    country = models.ForeignKey(ExportingCountry, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
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
    date_added = models.DateField()
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
    
class MonthlyProfit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateField()
    year = models.IntegerField()
    month = models.IntegerField()
    total_revenue = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    other_expences = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    profit = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'monthly_profit'
        verbose_name = 'Monthly Profit'
        verbose_name_plural = 'Monthly Profits'

    def __str__(self):
        return f'Monthly Profit {self.month} - {self.year}'
    
class MyProfit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateField()
    year = models.IntegerField()
    month = models.IntegerField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'groups__name__in': ['core_team', 'investor']})
    profit = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'my_profit'
        verbose_name = 'My Profit'
        verbose_name_plural = 'My Profits'

    def __str__(self):
        return f'My Profit {self.date_added}'
    
    def get_username(self):
        user_details = ""
        
        if CoreTeam.objects.filter(user=self.user).exists():
            instance = CoreTeam.objects.get(user=self.user)
            user_details = f'{instance.first_name} {instance.last_name}'
        elif Investors.objects.filter(user=self.user).exists():
            instance = Investors.objects.get(user=self.user)
            user_details = f'{instance.first_name} {instance.last_name}'
            
        return user_details