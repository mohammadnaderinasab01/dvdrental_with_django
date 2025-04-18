# Generated by Django 5.1.6 on 2025-02-15 04:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('staff_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=45)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('store_id', models.SmallIntegerField()),
                ('active', models.BooleanField()),
                ('username', models.CharField(max_length=16)),
                ('password', models.CharField(blank=True, max_length=40, null=True)),
                ('last_update', models.DateTimeField()),
                ('picture', models.BinaryField(blank=True, null=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='customer.address')),
            ],
            options={
                'db_table': 'staff',
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('store_id', models.AutoField(primary_key=True, serialize=False)),
                ('last_update', models.DateTimeField()),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='customer.address')),
                ('manager_staff', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='store.staff')),
            ],
            options={
                'db_table': 'store',
            },
        ),
    ]
