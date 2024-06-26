from dal import autocomplete
from django.forms.widgets import TextInput,Textarea,Select,DateInput,CheckboxInput,FileInput,PasswordInput
from django import forms
from .models import *


class ExecutiveForm(forms.ModelForm):
    re_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Re-enter Password'})
    )

    class Meta:
        model = Executive
        fields = ['first_name','last_name','email','phone','date_of_birth','state','country','image','address','zip','department','password','re_password']

        widgets = {
            'first_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter First Name'}), 
            'last_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Last Name'}), 
            'email': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Email'}), 
            'phone': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Phone Number'}), 
            'investment_amount': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Investment Amount'}), 
            'date_of_birth': TextInput(attrs={'class': 'required form-control','id':'date_of_birth','name':'date_of_birth','placeholder' : 'Enter Date of Birth'}), 
            'state': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter State'}), 
            'country': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Country'}), 
            'zip': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Zip'}), 
            'password': PasswordInput(attrs={'class': 'required form-control','placeholder' : 'Enter Password'}), 
            'image': FileInput(attrs={'class': 'form-control dropify'}),
            'address': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Address','rows':'5'}), 
            'department': Select(attrs={'class': 'required form-control'}), 
        }
        
    def clean_image(self):
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            if not (image_file.name.endswith(".jpg") or image_file.name.endswith(".png") or image_file.name.endswith(".jpeg")):
                raise forms.ValidationError("Only .jpg or .png files are accepted")
        return image_file


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')

        if password and re_password and password != re_password:
            raise forms.ValidationError("Passwords do not match")

        if password and len(password) < 8:
            raise forms.ValidationError("Please enter a minimum of 8 characters")

        if password and len(password) > 20:
            raise forms.ValidationError("Please enter a maximum of 20 characters for the password")

        return cleaned_data


class ExecutiveEditForm(forms.ModelForm):

    class Meta:
        model = Executive
        fields = ['first_name','last_name','email','phone','date_of_birth','state','country','image','address','zip','department']

        widgets = {
            'first_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter First Name'}), 
            'last_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Last Name'}), 
            'email': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Email'}), 
            'phone': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Phone Number'}), 
            'date_of_birth': TextInput(attrs={'class': 'required form-control','id':'date_of_birth','name':'birthday','placeholder' : 'Enter Date of Birth'}), 
            'state': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter State'}), 
            'country': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Country'}), 
            'zip': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Zip'}), 
            'image': FileInput(attrs={'class': 'form-control dropify'}),
            'address': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Address','rows':'5'}), 
            'department': Select(attrs={'class': 'required form-control'}), 
        }
        
    def clean_image(self):
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            if not (image_file.name.endswith(".jpg") or image_file.name.endswith(".png") or image_file.name.endswith(".jpeg")):
                raise forms.ValidationError("Only .jpg or .png files are accepted")
        return image_file