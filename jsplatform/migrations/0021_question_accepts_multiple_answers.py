# Generated by Django 3.1.8 on 2021-04-23 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0020_auto_20210422_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='accepts_multiple_answers',
            field=models.BooleanField(default=False),
        ),
    ]