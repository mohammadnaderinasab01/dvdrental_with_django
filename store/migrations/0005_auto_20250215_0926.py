# customer/migrations/0005_verify_staff_user_links.py
from django.db import migrations


def verify_staff_user_links(apps, schema_editor):
    Staff = apps.get_model('store', 'Staff')
    if Staff.objects.filter(user__isnull=True).exists():
        raise ValueError("Some customers are not linked to a user. Fix this before proceeding.")


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0004_staff_user'),
    ]

    operations = [
        migrations.RunPython(verify_staff_user_links),
    ]
