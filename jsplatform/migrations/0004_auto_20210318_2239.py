# Generated by Django 3.1.7 on 2021-03-18 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0003_examprogress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examprogress',
            name='completed_exercises',
            field=models.ManyToManyField(blank=True, related_name='completed_in_exams', to='jsplatform.Exercise'),
        ),
    ]
