# Generated by Django 3.0.5 on 2020-05-08 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20200429_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(max_length=200000),
        ),
    ]
