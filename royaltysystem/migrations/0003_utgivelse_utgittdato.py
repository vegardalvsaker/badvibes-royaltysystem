# Generated by Django 2.0.7 on 2019-02-11 09:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('royaltysystem', '0002_auto_20190210_0112'),
    ]

    operations = [
        migrations.AddField(
            model_name='utgivelse',
            name='utgittdato',
            field=models.DateField(default=datetime.datetime(2019, 2, 11, 9, 57, 23, 942534, tzinfo=utc)),
        ),
    ]
