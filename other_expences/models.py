from django.db import models

from main.models import BaseModel

# Create your models here.
class ExpenceTypes(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True)
    
    class Meta:
        db_table = 'expence_type'
        verbose_name = ('Expence Type')
        verbose_name_plural = ('Expence Type')
    
    def __str__(self):
        return str(self.name)

class OtherExpences(BaseModel):
    remark = models.CharField(max_length=200,blank=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expence_type = models.ForeignKey(ExpenceTypes,on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    
    class Meta:
        db_table = 'other_expences'
        verbose_name = ('Other Expences')
        verbose_name_plural = ('Other Expences')