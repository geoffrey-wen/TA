# Generated by Django 3.0.9 on 2020-10-20 07:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0026_report_point'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100, null=True)),
                ('content', models.TextField(null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('image', models.ImageField(null=True, upload_to='report_images')),
                ('collaborator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report.Report')),
            ],
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to='report_images')),
                ('collaboration', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='report.Collaboration')),
                ('report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='report.Report')),
            ],
        ),
    ]
