# Generated by Django 3.1.12 on 2021-06-12 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0028_auto_20210612_1419'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterField(
            model_name='examprogress',
            name='completed_items_count',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
