# Generated by Django 4.2.19 on 2025-02-25 12:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0004_customuser_user_locations_alter_customuser_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
