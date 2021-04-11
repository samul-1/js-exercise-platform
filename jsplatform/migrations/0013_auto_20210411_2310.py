# Generated by Django 3.1.7 on 2021-04-11 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jsplatform', '0012_auto_20210411_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='examprogress',
            name='served_for_current_category',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('amount', models.PositiveIntegerField(default=1)),
                ('item_type', models.CharField(choices=[('q', 'QUESTIONS'), ('e', 'EXERCISES')], max_length=1)),
                ('exam', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jsplatform.exam')),
            ],
        ),
        migrations.AddField(
            model_name='examprogress',
            name='current_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_in_exams', to='jsplatform.category'),
        ),
        migrations.AddField(
            model_name='examprogress',
            name='exhausted_categories',
            field=models.ManyToManyField(blank=True, to='jsplatform.Category'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercises', to='jsplatform.category'),
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='jsplatform.category'),
        ),
    ]
