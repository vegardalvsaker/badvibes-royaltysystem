# Generated by Django 2.0.7 on 2019-02-11 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royaltysystem', '0006_auto_20190211_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utgivelseformat',
            name='fysisk_format_type',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
