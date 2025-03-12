from celery import shared_task
from django.conf import settings
import smtplib
from payment.models import Rental
from django.utils import timezone
from datetime import timedelta
from customer.models import Customer
from admin_panel.models import SiteConfig


@shared_task
def send_inventory_rental_overdue_email():
    try:
        overdue_days = int(SiteConfig.objects.get_config(key='FILM_INVENTORY_OVERDUE_DAYS', default=30))
    except ValueError:
        print('an error occurred')

    last_30_days = timezone.now().date() - timedelta(days=overdue_days)
    overdue_rentals = Rental.objects.filter(return_date__isnull=True,
                                            rental_date__lt=last_30_days).select_related('customer', 'inventory', 'staff', 'staff__store')
    for overdue_rental in overdue_rentals:
        customer = overdue_rental.customer
        subject = "DVDRental - Rental Overdue"
        message = f"Hi {customer.first_name},\n\nYour rental duration for rental with id: {overdue_rental.rental_id} for inventory with id: {overdue_rental.inventory.inventory_id} has been expired.\nSo please immediately turn the inventory back to the store with id: {overdue_rental.staff.store_id}"
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


@shared_task
def inactive_customers_activity_email_notifier():
    try:
        inactive_days_threshold = int(SiteConfig.objects.get_config(key='INACTIVE_DAYS_THRESHOLD', default=60))
    except ValueError:
        print('an error occurred')

    last_60_days = timezone.now().date() - timedelta(days=inactive_days_threshold)
    inactive_customers = Customer.objects.filter(
        rental__rental_date__lt=last_60_days,
        rental__return_date__lt=last_60_days)
    for cst in inactive_customers:
        subject = "DVDRental - Missing You"
        message = f"Hi Dear {cst.first_name},\n\nIt's now over 60 days that we do not see you in our app.\nThis is Just a message for you to see that \"we miss you :)\". Just come back soon... :)"
        try:
            connection = smtplib.SMTP(settings.MAIL_SERVER_HOST)
            connection.starttls()
            connection.login(user=settings.NOTIFIER_EMAIL_ADDRESS, password=settings.NOTIFIER_EMAIL_PASSWORD)
            connection.sendmail(
                from_addr=settings.NOTIFIER_EMAIL_ADDRESS,
                to_addrs=cst.email,
                msg=f"Subject:{subject}\n\n{message}")
            connection.close()
        except smtplib.SMTPAuthenticationError as e:
            print(f"Failed to send email to {cst.email}: {e}")
