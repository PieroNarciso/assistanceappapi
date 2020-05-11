# Generated by Django 3.0.4 on 2020-05-11 00:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistance', '0002_auto_20200323_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assistance',
            name='check_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='assistance',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_data', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='numcode',
            name='code',
            field=models.IntegerField(default=652856),
        ),
    ]