# Generated by Django 4.2.13 on 2024-05-15 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adverts', '0005_alter_emailreferee_application_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RefereeEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adverts.application')),
                ('referee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adverts.reference')),
            ],
        ),
    ]
