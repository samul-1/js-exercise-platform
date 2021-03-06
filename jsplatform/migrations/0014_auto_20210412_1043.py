# Generated by Django 3.1.7 on 2021-04-12 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0013_auto_20210411_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='tmp_uuid',
            field=models.UUIDField(blank=True, null=True, verbose_name='frontend_uuid'),
        ),
        migrations.AlterField(
            model_name='category',
            name='exam',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categories', to='jsplatform.exam'),
        ),
    ]
