# In commands.py within your app

from django.core.management.base import BaseCommand
from django.utils import timezone
from profit.views import calculate_monthly_profit, calculate_profit, distribute_profits, profit_calculation
from purchase.models import Purchase
from sales.models import Sales

class Command(BaseCommand):
    help = 'Calculate profit for a given date and update Daily Profit instance'

    def handle(self, *args, **kwargs):
        purchases = Purchase.objects.filter(is_deleted=False)
        for p in purchases:
            profit_calculation(p.date)
            print(f"purchase {p.date}")
        
        sales = Sales.objects.filter(is_deleted=False)
        for s in sales:
            profit_calculation(s.date)
            print(f"sales {s.date}")

        self.stdout.write(self.style.SUCCESS(f'Profit calculated and updated successfully'))
