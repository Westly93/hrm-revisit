# Generated by Django 4.2.13 on 2024-05-15 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adverts', '0008_rename_app_emailreferee_application_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailreferee',
            name='application',
        ),
        migrations.RemoveField(
            model_name='emailreferee',
            name='referee',
        ),
        migrations.AddField(
            model_name='emailreferee',
            name='application_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='emailreferee',
            name='referee_id',
            field=models.IntegerField(null=True),
        ),
    ]
