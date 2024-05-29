from django.forms.widgets import TextInput,FileInput,Textarea
from django import forms

from . models import *
from dal import autocomplete
        
class PurchasePartyForm(forms.ModelForm):

    class Meta:
        model = PurchaseParty
        fields = ['first_name','last_name','email','phone','gst_no','date_of_birth','address','state','country','zip','image']

        widgets = {
            'first_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter First Name'}), 
            'last_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Last Name'}), 
            'email': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Email'}), 
            'phone': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Phone Number'}), 
            'gst_no': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter GST No'}), 
            'date_of_birth': TextInput(attrs={'class': 'required form-control','id':'date_of_birth','name':'date_of_birth','placeholder' : 'Enter Date of Birth'}), 
            'address': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Address','rows':'5'}),
            'state': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter State'}), 
            'country': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Country'}),
            'zip': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Zip'}), 
            'image': FileInput(attrs={'class': 'form-control dropify'}),
        }
        
    def clean_image(self):
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            if not (image_file.name.endswith(".jpg") or image_file.name.endswith(".png") or image_file.name.endswith(".jpeg")):
                raise forms.ValidationError("Only .jpg or .png files are accepted")
        return image_file
    
    def clean_email(self):
        email = self.cleaned_data['email']
        instance = self.instance
        if instance and instance.email == email:
            return email  # If email hasn't changed, return as is

        user_exists = User.objects.filter(username=email).exists()
        if user_exists:
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        instance = self.instance
        if instance and instance.phone == phone:
            return phone  # If phone number hasn't changed, return as is

        if PurchaseParty.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already in use.")
        return phone