# Generated by Django 4.2.13 on 2024-05-15 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_useraccount_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
