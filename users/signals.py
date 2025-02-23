# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError
from customer.models import Customer
from .models import User
from datetime import date


@receiver(post_save, sender=User)
def create_customer_for_user(sender, instance, created, **kwargs):
    """
    When a new User is created, create a corresponding Customer.
    """
    if created and instance.is_customer:
        Customer.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'create_date': date.today(),
                'activebool': True,
                'active': instance.is_active,
            }
        )
    elif not created and instance.is_customer:
        try:
            fields_set = kwargs.get('update_fields')
            if kwargs and fields_set and list(fields_set) and \
                len(list(fields_set)) == 1 and list(fields_set)[0] == 'last_login':
                return

            customer = Customer.objects.get(user=instance)
            # Update the customer fields
            customer.first_name = instance.first_name
            customer.last_name = instance.last_name
            customer.email = instance.email
            customer.create_date = date.today()
            customer.activebool = True
            customer.active = instance.is_active
            customer.save()
        except Customer.DoesNotExist:
            instance.delete()
            # raise ValidationError(
            #     f'User {instance.email} has been deleted because the corresponding Customer does not exist.')
