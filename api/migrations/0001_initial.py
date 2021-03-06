# Generated by Django 3.1.1 on 2020-09-14 03:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attending', models.ManyToManyField(blank=True, related_name='class_rooms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Phase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('timer', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.IntegerField(choices=[(1, 'Change phase'), (2, 'Join'), (3, 'Leave')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('timer', models.IntegerField(default=0)),
                ('class_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='api.classroom')),
                ('to_phase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.phase')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('default_phase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='start_of_course', to='api.phase')),
                ('phases', models.ManyToManyField(blank=True, to='api.Phase')),
            ],
        ),
        migrations.AddField(
            model_name='classroom',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='class_rooms', to='api.course'),
        ),
    ]
