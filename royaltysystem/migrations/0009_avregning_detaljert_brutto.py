# Generated by Django 2.0.7 on 2019-02-11 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royaltysystem', '0008_auto_20190211_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='avregning_detaljert',
            name='brutto',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]