# Generated by Django 3.0.9 on 2020-08-19 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0006_dummyoffer_dummy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dummyoffer',
            name='dummy',
        ),
    ]