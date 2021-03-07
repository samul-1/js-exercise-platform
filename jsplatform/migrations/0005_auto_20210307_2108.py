# Generated by Django 3.1.7 on 2021-03-07 21:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0004_user_is_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercises', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL),
        ),
    ]