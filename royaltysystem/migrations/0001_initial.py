# Generated by Django 2.0.7 on 2019-02-10 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('contract_since', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Avregning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periode', models.CharField(max_length=7)),
                ('bruttoinntekt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('royalty_prosent', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Avregning_Detaljert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periode', models.CharField(max_length=7)),
                ('kilde', models.CharField(max_length=20)),
                ('antall', models.IntegerField()),
                ('inntekter', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kostnader', models.DecimalField(decimal_places=2, max_digits=10)),
                ('dl_utgivelse', models.IntegerField()),
                ('dl_spor', models.IntegerField()),
                ('streams', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Utgivelse',
            fields=[
                ('katalognr', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('navn', models.CharField(max_length=200)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royaltysystem.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='UtgivelseFormat',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('format', models.CharField(max_length=10)),
                ('format_type', models.CharField(max_length=20)),
                ('utgivelse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royaltysystem.Utgivelse')),
            ],
        ),
        migrations.AddField(
            model_name='avregning_detaljert',
            name='utgivelseFormat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royaltysystem.UtgivelseFormat'),
        ),
        migrations.AddField(
            model_name='avregning',
            name='utgivelse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royaltysystem.Utgivelse'),
        ),
    ]
