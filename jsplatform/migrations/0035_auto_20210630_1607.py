# Generated by Django 3.1.12 on 2021-06-30 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0034_frontenderror'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontenderror',
            name='component_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='frontenderror',
            name='route',
            field=models.TextField(blank=True, null=True),
        ),
    ]
