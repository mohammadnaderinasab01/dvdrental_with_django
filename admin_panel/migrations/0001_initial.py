# Generated by Django 5.1.6 on 2025-03-11 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, unique=True)),
                ('value', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
            ],
        ),
    ]
