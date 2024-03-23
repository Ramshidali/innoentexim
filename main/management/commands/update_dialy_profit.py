# In commands.py within your app

from django.core.management.base import BaseCommand
from django.utils import timezone
from profit.views import calculate_monthly_profit, calculate_profit, distribute_profits

class Command(BaseCommand):
    help = 'Calculate profit for a given date and update Daily Profit instance'

    def handle(self, *args, **kwargs):
        # Get today's date
        today_date = timezone.now().date()

        # Calculate profit for today's date
        profit = calculate_profit(today_date)
        
        year = today_date.year
        month = today_date.month
        calculate_monthly_profit(year, month)
        
        distribute_profits(year, month)

        self.stdout.write(self.style.SUCCESS(f'Profit calculated and updated successfully for {today_date}: {profit}'))
