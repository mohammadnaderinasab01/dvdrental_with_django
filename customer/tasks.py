from celery import shared_task
from django.conf import settings
from .models import Customer
import smtplib


@shared_task
def send_welcome_email(customer_id):
    customer = Customer.objects.get(customer_id=customer_id)
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
        print(f"Failed to send email to {customer.email}: {e}")
