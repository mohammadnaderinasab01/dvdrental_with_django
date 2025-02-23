# customer/migrations/0005_verify_customer_user_links.py
from django.db import migrations


def verify_customer_user_links(apps, schema_editor):
    Customer = apps.get_model('customer', 'Customer')
    if Customer.objects.filter(user__isnull=True).exists():
        raise ValueError("Some customers are not linked to a user. Fix this before proceeding.")


class Migration(migrations.Migration):
    dependencies = [
        ('customer', '0004_customer_user'),
    ]

    operations = [
        migrations.RunPython(verify_customer_user_links),
    ]
