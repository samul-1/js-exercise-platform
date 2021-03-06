# Generated by Django 3.1.7 on 2021-03-18 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jsplatform', '0002_auto_20210317_0948'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_exercises', models.ManyToManyField(blank=True, null=True, related_name='completed_in_exams', to='jsplatform.Exercise')),
                ('current_exercise', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_in_exams', to='jsplatform.exercise')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jsplatform.exam')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams_progress', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
