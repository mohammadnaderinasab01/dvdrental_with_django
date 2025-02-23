from django.core.exceptions import ValidationError


def only_int(value): 
    if value.isdigit() == False:
        raise ValidationError('NationalID contains characters')