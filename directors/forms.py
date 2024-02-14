from dal import autocomplete
from django.forms.widgets import TextInput,Textarea,Select,DateInput,CheckboxInput,FileInput,PasswordInput
from django import forms
from . models import *

class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Departments
        fields = ['name','description']

        widgets = {
            'name': TextInput(attrs={'class': 'multisteps-form__input required form-control','placeholder' : 'Enter Name'}),
            'description': Textarea(attrs={'class': 'required form-control text-area','placeholder' : 'Enter Description','rows':'2'}), 
        }
        
        
class DirectorForm(forms.ModelForm):

    class Meta:
        model = Directors
        fields = ['user','department']

        widgets = {
            'user': Select(attrs={'class': 'required form-control'}),
            'department': Select(attrs={'class': 'required form-control'}), 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label_from_instance = self.get_user_label

    def get_user_label(self, user):
        if CoreTeam.objects.filter(user=user, is_deleted=False).exists():
            instance = CoreTeam.objects.get(user=user, is_deleted=False)
            return f"{instance.employee_id}-{instance.first_name} {instance.last_name}"
        elif Investors.objects.filter(user=user, is_deleted=False).exists():
            instance = Investors.objects.get(user=user, is_deleted=False)
            return f"{instance.investor_id}-{instance.first_name} {instance.last_name}"
        else:
            return user.username