# In commands.py within your app

from django.core.management.base import BaseCommand
from django.utils import timezone
from profit.views import calculate_monthly_profit, calculate_profit, distribute_profits, profit_calculation

class Command(BaseCommand):
    help = 'Calculate profit for a given date and update Daily Profit instance'

    def handle(self, *args, **kwargs):
        
        profit_calculation()

        self.stdout.write(self.style.SUCCESS(f'Profit calculated and updated successfully'))
