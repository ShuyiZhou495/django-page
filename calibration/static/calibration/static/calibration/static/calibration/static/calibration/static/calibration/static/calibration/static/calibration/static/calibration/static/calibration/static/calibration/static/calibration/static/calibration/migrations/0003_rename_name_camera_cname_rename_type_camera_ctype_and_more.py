# Generated by Django 4.0.2 on 2022-03-02 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calibration', '0002_camera_name_lidar_name_alter_camera_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='camera',
            old_name='name',
            new_name='cname',
        ),
        migrations.RenameField(
            model_name='camera',
            old_name='type',
            new_name='ctype',
        ),
        migrations.RenameField(
            model_name='lidar',
            old_name='name',
            new_name='cname',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='para',
        ),
        migrations.AddField(
            model_name='camera',
            name='cb1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='cfx',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='cfy',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='ck1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='ck2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='ck3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='cp1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='cp2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='cx',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='cy',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='camera',
            name='mask',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
