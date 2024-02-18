#django
from django.db import models
from django.contrib.auth.models import User
#third party
from versatileimagefield.fields import VersatileImageField
#local
from main.models import BaseModel
from main.variables import phone_regex

# Create your models here.
class SalesParty(BaseModel):
    party_id = models.CharField(max_length=15)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, validators=[phone_regex], unique=True)
    date_of_birth = models.DateField()
    gst_no = models.CharField(max_length=15)
    address = models.TextField()
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    zip = models.CharField(max_length=200)
    image = VersatileImageField('Image', upload_to="sales_party/profile_pic", blank=True, null=True)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    
    class Meta:
        db_table = 'sales_party'
        verbose_name = ('Sales Party')
        verbose_name_plural = ('Sales Party')
        
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_fullname(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_initial(self):
        first_name = self.first_name[0] if self.first_name else ''
        last_name = self.last_name[0] if self.last_name else ''
        return first_name + last_name