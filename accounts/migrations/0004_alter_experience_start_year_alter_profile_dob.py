# Generated by Django 4.2.13 on 2024-05-14 17:03

import accounts.models
import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_experience_start_year_alter_profile_dob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='start_year',
            field=models.DateField(validators=[django.core.validators.MaxValueValidator(datetime.date(2024, 5, 14))]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='dob',
            field=models.DateField(blank=True, null=True, validators=[accounts.models.validate_age_range]),
        ),
    ]