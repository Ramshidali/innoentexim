from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from coreteam.models import CoreTeam
from investors.models import Investors

from versatileimagefield.fields import VersatileImageField

from main.models import BaseModel
from main.variables import phone_regex

# Create your models here.
class Departments(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True)
    
    class Meta:
        db_table = 'directors_department'
        verbose_name = ('Directors Department')
        verbose_name_plural = ('Directors Department')
    
    def __str__(self):
        return str(self.name)

class Directors(BaseModel):
    user = models.OneToOneField(User,limit_choices_to={'is_superuser': False, 'groups__name__in': ["investor"]},on_delete=models.CASCADE)
    department = models.ForeignKey(Departments,on_delete=models.CASCADE,blank=True,null=True, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'directors'
        verbose_name = ('Directors')
        verbose_name_plural = ('Directors')
        
    def __str__(self):
        if CoreTeam.objects.filter(user=self.user,is_deleted=False).exists():
            instance = CoreTeam.objects.get(user=self.user,is_deleted=False)
            user_details = f'{instance.employee_id}-{instance.first_name} {instance.last_name}'
        elif Investors.objects.filter(user=self.user,is_deleted=False).exists():
            instance = Investors.objects.get(user=self.user,is_deleted=False)
            user_details = f'{instance.investor_id}-{instance.first_name} {instance.last_name}'
        else:
          user_details = self.user.username
            
        return user_details
    
    # def get_fullname(self):
    #     return f'{self.first_name} {self.last_name}'
    
    # def get_initial(self):
    #     first_name = self.first_name[0] if self.first_name else ''
    #     last_name = self.last_name[0] if self.last_name else ''
    #     return first_name + last_name