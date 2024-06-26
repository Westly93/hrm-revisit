# Generated by Django 4.2.13 on 2024-05-12 13:23

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_useraccount_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='start_year',
            field=models.DateField(validators=[django.core.validators.MaxValueValidator(datetime.date(2024, 5, 12))]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='dob',
            field=models.DateField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(datetime.date(2008, 5, 16))]),
        ),
    ]
