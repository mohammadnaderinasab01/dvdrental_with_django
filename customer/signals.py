# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_welcome_email
from .models import Customer


@receiver(post_save, sender=Customer)
def send_welcome_email_signal(sender, instance, created, **kwargs):
    print('my new signal started!')
    if created:
        send_welcome_email.delay(instance.customer_id)
