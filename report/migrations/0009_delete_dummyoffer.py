# Generated by Django 3.0.9 on 2020-08-19 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_remove_dummyoffer_discount'),
    ]

    operations = [
        migrations.DeleteModel(
            name='dummyoffer',
        ),
    ]
