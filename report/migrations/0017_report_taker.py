# Generated by Django 3.0.9 on 2020-09-11 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0016_report_progress'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='taker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reporttaken_set', to=settings.AUTH_USER_MODEL),
        ),
    ]