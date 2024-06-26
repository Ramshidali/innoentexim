#Standard
import string
import random
import random
import string
from cryptography.fernet import Fernet
#Django
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.core.mail import EmailMessage, EmailMultiAlternatives
#Third Party
from mailqueue.models import MailerMessage
from random import randint


def generate_unique_id(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_form_errors(args,formset=False):
    i = 1
    message = ""
    if not formset:
        for field in args:	
            if field.errors:
                message += "\n"
                message += field.label + " : "
                message += str(field.errors)

        for err in args.non_field_errors():
            message += str(err)
    elif formset:
        for form in args:
            for field in form:
                if field.errors:
                    message += "\n"
                    message += field.label + " : "
                    message += str(field.errors)
            for err in form.non_field_errors():
                message += str(err)

    message = message.replace("<li>", "")
    message = message.replace("</li>", "")
    message = message.replace('<ul class="errorlist">', "")
    message = message.replace("</ul>", "")
    return message

def generate_member_form_errors(args,formset=False):
    i = 1
    message = ""
    if not formset:
        for field in args:
            if field.errors:
                message += "\n"
                message += field.name + " : "
                message += str(field.errors)

        for err in args.non_field_errors():
            message += str(err)
    elif formset:
        for form in args:
           
            for field in form:
                if field.errors:
                    message += "\n"
                    message += field.name + " : "
                    message += str(field.errors)
            for err in form.non_field_errors():
                message += str(err)

    message = message.replace("<li>", "")
    message = message.replace("</li>", "")
    message = message.replace('<ul class="errorlist">', "")
    message = message.replace("</ul>", "")
    return message
    

def get_auto_id(model):
    auto_id = 1
    try:
        latest_auto_id =  model.objects.all().order_by("-date_added")[:1]
        if latest_auto_id:
            for auto in latest_auto_id:
                auto_id = auto.auto_id + 1
    except:
        pass
    return auto_id


def get_current_role(request):
    # Ensure the user is authenticated and active before proceeding
    if request.user.is_authenticated and request.user.is_active:
        # Get all user groups and print their names
        user_groups = request.user.groups.all()
        for group in user_groups:
            print(group.name)
    
    # Initialize all role flags to False
    is_superadmin = False
    is_staff = False
    is_core_team = False
    is_investor = False
    is_executive = False
    is_director = False
    is_sales = False
    is_purchase = False
    
    # List to collect all roles
    roles = []
    
    # If the user is authenticated, determine their roles
    if request.user.is_authenticated:
        # Check if the user is a superadmin
        is_superadmin = request.user.is_superuser and request.user.is_active
        if is_superadmin:
            roles.append("superadmin")
        
        # Get all group names associated with the user
        group_names = request.user.groups.values_list('name', flat=True)
        print(list(group_names))  # Convert to list for better readability in print output
        
        # Check membership in each group and add to roles list
        if 'staff' in group_names:
            roles.append('staff')
        if 'core_team' in group_names:
            roles.append('core_team')
        if 'investor' in group_names:
            roles.append('investor')
        if 'executive' in group_names:
            roles.append('executive')
        if 'director' in group_names:
            roles.append('director')
        if 'sales' in group_names:
            roles.append('sales')
        if 'purchase' in group_names:
            roles.append('purchase')
    
    # Determine the current role by concatenating roles
    current_role = ', '.join(roles) if roles else "user"  # Default role if no specific roles match
    
    print(current_role)  # Print the determined role
    
    return current_role



def randomnumber(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def paginate(instances, request):
    paginator = Paginator(instances, 20)
    page_number = request.GET.get('page')
    instances = paginator.get_page(page_number)

    return instances


def get_otp(size=4, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def load_key():
    key = getattr(settings, "PASSWORD_ENCRYPTION_KEY", None)
    if key:
        return key
    else:
        raise ImproperlyConfigured("No configuration  found in your PASSWORD_ENCRYPTION_KEY setting.")


def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return(encrypted_message.decode("utf-8"))


def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message.encode())
    return decrypted_message.decode()

    
    
def send_email(subject, to_address, content, mail_html, bcc_address=settings.DEFAULT_BCC_EMAIL, app="mrm", reply_to_address=settings.DEFAULT_REPLY_TO_EMAIL, attachment=True):
    # print("send fun")

    if attachment:
        email = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [to_address], bcc=[bcc_address], reply_to=[reply_to_address])
        email.attach_alternative(mail_html, "text/html")
        email.send()
    else:
        new_message = MailerMessage()
        new_message.subject = subject
        new_message.to_address = to_address
        if bcc_address:
            new_message.bcc_address = bcc_address
        new_message.from_address = settings.DEFAULT_FROM_EMAIL
        new_message.content = content
        new_message.app = app
        new_message.reply_to = reply_to_address
        new_message.save()
        
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False