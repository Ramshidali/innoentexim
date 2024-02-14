from django.db import models
from django.contrib.auth.models import User

from versatileimagefield.fields import VersatileImageField

from main.models import BaseModel
from main.variables import phone_regex

# Create your models here.
class Investors(BaseModel):
    investor_id = models.CharField(max_length=100)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, validators=[phone_regex], unique=True)
    date_of_birth = models.DateField()
    address = models.TextField()
    investment_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    password = models.CharField(max_length=256,null=True,blank=True)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    zip = models.CharField(max_length=200)
    
    image = VersatileImageField('Image', upload_to="core_team/profile_pic", blank=True, null=True)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    
    class Meta:
        db_table = 'invester'
        verbose_name = ('Investers')
        verbose_name_plural = ('Investers')
        
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_fullname(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_initial(self):
        first_name = self.first_name[0] if self.first_name else ''
        last_name = self.last_name[0] if self.last_name else ''
        return first_name + last_name