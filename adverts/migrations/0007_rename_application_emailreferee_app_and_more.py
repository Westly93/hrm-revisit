# Generated by Django 4.2.13 on 2024-05-15 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adverts', '0006_refereeemail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailreferee',
            old_name='application',
            new_name='app',
        ),
        migrations.RenameField(
            model_name='emailreferee',
            old_name='referee',
            new_name='ref',
        ),
        migrations.DeleteModel(
            name='RefereeEmail',
        ),
    ]
