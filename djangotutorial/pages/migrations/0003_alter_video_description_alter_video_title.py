# Generated by Django 4.2.20 on 2025-03-30 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_remove_video_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='description',
            field=models.CharField(max_length=5000),
        ),
        migrations.AlterField(
            model_name='video',
            name='title',
            field=models.CharField(max_length=1000),
        ),
    ]
