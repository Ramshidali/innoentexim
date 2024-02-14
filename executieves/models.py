from django.db import models
from django.contrib.auth.models import User
from directors.models import Departments

from versatileimagefield.fields import VersatileImageField

from main.models import BaseModel
from main.variables import phone_regex

# Create your models here.
class Executive(BaseModel):
    employee_id = models.CharField(max_length=100)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, validators=[phone_regex], unique=True)
    date_of_birth = models.DateField()
    address = models.TextField()
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    zip = models.CharField(max_length=200)
    password = models.CharField(max_length=256)
    image = VersatileImageField('Image', upload_to="core_team/profile_pic", blank=True, null=True)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    department = models.ForeignKey(Departments,on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'executives'
        verbose_name = ('Executives')
        verbose_name_plural = ('Executives')
        
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_fullname(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_initial(self):
        first_name = self.first_name[0] if self.first_name else ''
        last_name = self.last_name[0] if self.last_name else ''
        return first_name + last_name