#standerd
import json
import random
import datetime
from datetime import date, timedelta
#django
from django.urls import reverse
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,Group
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, HttpResponse
# third party
#local
from main.decorators import role_required

# Create your views here.
@login_required
def app(request):
  
    return HttpResponseRedirect(reverse('main:index'))

# Create your views here.
@login_required
# @role_required(['superadmin','core_team','director'])
def index(request):
    today_date = timezone.now().date()
    last_month_start = (today_date - timedelta(days=today_date.day)).replace(day=1)
    
    context = {
        'page_title' : 'Dashboard | Innoentexim',
        'is_dashboard': True,   
    }
  
    return render(request,'admin_panel/index.html', context)