# Generated by Django 3.1.12 on 2021-06-12 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0024_examprogress_pdf_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examprogress',
            name='completed_exercises',
        ),
        migrations.RemoveField(
            model_name='examprogress',
            name='completed_questions',
        ),
        migrations.AddField(
            model_name='examprogress',
            name='completed_items_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='ExamCompletedQuestionsThroughModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField()),
                ('completed_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jsplatform.question')),
                ('exam_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jsplatform.examprogress')),
            ],
        ),
        migrations.CreateModel(
            name='ExamCompletedExercisesThroughModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField()),
                ('completed_exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jsplatform.exercise')),
                ('exam_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jsplatform.examprogress')),
            ],
        ),
    ]
