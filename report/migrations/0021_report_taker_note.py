# Generated by Django 3.0.9 on 2020-09-13 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0020_remove_report_taker_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='taker_note',
            field=models.TextField(null=True),
        ),
    ]
