from celery import shared_task
from django.conf import settings
import smtplib
from payment.models import Rental
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_inventory_rental_overdue_email():
    last_30_days = timezone.now().date() - timedelta(days=30)
    overdue_rentals = Rental.objects.filter(return_date__isnull=True,
                                            rental_date__lte=last_30_days).select_related('customer', 'inventory', 'staff', 'staff__store')
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
