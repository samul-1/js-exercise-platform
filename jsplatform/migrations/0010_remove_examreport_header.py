# Generated by Django 3.1.7 on 2021-04-04 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0009_examreport_header'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examreport',
            name='header',
        ),
    ]
