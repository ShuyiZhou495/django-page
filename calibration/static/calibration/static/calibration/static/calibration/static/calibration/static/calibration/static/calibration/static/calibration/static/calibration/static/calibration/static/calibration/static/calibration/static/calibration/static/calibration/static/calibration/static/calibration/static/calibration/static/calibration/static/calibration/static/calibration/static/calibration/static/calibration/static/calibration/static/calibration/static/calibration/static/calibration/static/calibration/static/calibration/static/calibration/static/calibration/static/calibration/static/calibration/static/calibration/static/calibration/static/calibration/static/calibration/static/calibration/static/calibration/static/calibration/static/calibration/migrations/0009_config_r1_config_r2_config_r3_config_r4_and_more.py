# Generated by Django 4.0.2 on 2022-03-04 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calibration', '0008_remove_config_scan_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='R1',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='R2',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='R3',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='R4',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='degree',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='ini_type',
            field=models.CharField(choices=[('quaternion', 'quaternion'), ('euler', 'euler')], default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='config',
            name='t1',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='t2',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='t3',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='config',
            name='selected',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
