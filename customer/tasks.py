from celery import shared_task
from django.conf import settings
from .models import Customer
import smtplib
import logging
from django.utils import timezone

# Configure the logger
logger = logging.getLogger('customer.tasks')


@shared_task
def send_welcome_email(customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        logger.error(f'{timezone.now()} --- SEND_WELCOME_EMAIL --- customer with id: {customer_id} not found.')
    subject = "Welcome to Our DVD Rental Service!"
    message = f"Hi {customer.first_name},\n\nThank you for signing up with us."
    try:
        connection = smtplib.SMTP(settings.MAIL_SERVER_HOST)
        connection.starttls()
        connection.login(user=settings.NOTIFIER_EMAIL_ADDRESS, password=settings.NOTIFIER_EMAIL_PASSWORD)
        connection.sendmail(
            from_addr=settings.NOTIFIER_EMAIL_ADDRESS,
            to_addrs=customer.email,
            msg=f"Subject:{subject}\n\n{message}")
        connection.close()
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"{timezone.now()} --- SEND_WELCOME_EMAIL --- Failed to send email to {customer.email}: {e}")
