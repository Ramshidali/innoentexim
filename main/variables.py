from django.core.validators import RegexValidator


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', message="Not an valid number")