# Generated by Django 5.1.3 on 2025-04-15 14:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='userdb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.CharField(editable=False, max_length=12, unique=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('gender', models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Non-Binary')], default=1)),
                ('dob', models.DateField()),
                ('age', models.IntegerField(default=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='userchat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.TextField()),
                ('response', models.TextField()),
                ('userimage', models.ImageField(upload_to='media/')),
                ('genimage', models.ImageField(upload_to='media/')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eatright.userdb')),
            ],
        ),
        migrations.CreateModel(
            name='useraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dishname', models.CharField(max_length=100)),
                ('action', models.CharField(max_length=10)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eatright.userdb')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('userid', 'dishname'), name='unique_user_dish')],
            },
        ),
        migrations.CreateModel(
            name='userfavoritedishes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dishname', models.CharField(max_length=100)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eatright.userdb')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('userid', 'dishname'), name='unique_fav_dish')],
            },
        ),
    ]
