from datetime import date
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from innoentexim import settings
from main.functions import send_email
from profit.models import ExchangeRate

class Command(BaseCommand):
    help = 'Update ExchangeRate status based on start and end dates'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', type=str, help='Base URL for constructing absolute URLs in emails')

    def handle(self, *args, **kwargs):
        now = timezone.now()  # Make now offset-aware
        base_url = kwargs['base_url']

        for exchange_rate in ExchangeRate.objects.all():
            if exchange_rate.start_date <= now <= exchange_rate.end_date:
                exchange_rate.is_active = True
                
                # Calculate days left until the end date
                days_left = (exchange_rate.end_date - now).days
                
                # Check if there are only 3 days left until the end date
                if days_left <= 3:
                    # Send email to admin
                    mail_html = render_to_string('mail_templates/exchange_date_remider.html', {'data': exchange_rate, 'days_left': days_left, 'base_url': base_url})
                    if settings.SERVER :
                        
                        mail_message = strip_tags(mail_html)
                        if days_left == 0:
                            subject = "Reminder: ExchangeRate ends tomorrow"
                        else:
                            subject = "Reminder: Only {} days left for ExchangeRate".format(days_left)
                        
                        send_email(subject, "aliramshid@gmail.com", mail_message, mail_html)
                    else:
                        print(mail_html)           
            else:
                exchange_rate.is_active = False
                if date.today() == exchange_rate.end_date.date():
                    # If today is the end date, send email
                    mail_context = {'data': exchange_rate}
                    if base_url:
                        mail_context['base_url'] = base_url

                    mail_html = render_to_string('mail_templates/exchange_date_expired.html', mail_context)

                    if settings.SERVER:
                        mail_message = strip_tags(mail_html)
                        send_email("ExchangeRate ends today",
                                   "aliramshid@gmail.com", mail_message, mail_html)
                    else:
                        print(mail_html)
                print("today")
            exchange_rate.save()
        self.stdout.write(self.style.SUCCESS('ExchangeRate statuses updated successfully'))

