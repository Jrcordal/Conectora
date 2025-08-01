# Generated by Django 5.2 on 2025-07-18 14:10

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('timezone', models.CharField(choices=[('UTC-12:00', 'UTC−12:00 — Baker Island'), ('UTC-11:00', 'UTC−11:00 — Niue'), ('UTC-10:00', 'UTC−10:00 — Hawaii'), ('UTC-09:00', 'UTC−09:00 — Alaska'), ('UTC-08:00', 'UTC−08:00 — Pacific Time (US & Canada)'), ('UTC-07:00', 'UTC−07:00 — Mountain Time (US & Canada)'), ('UTC-06:00', 'UTC−06:00 — Central Time (US & Mexico)'), ('UTC-05:00', 'UTC−05:00 — Colombia, Peru, Eastern US'), ('UTC-04:00', 'UTC−04:00 — Venezuela, Bolivia'), ('UTC-03:00', 'UTC−03:00 — Argentina, Uruguay, Brazil (East)'), ('UTC-02:00', 'UTC−02:00 — Mid-Atlantic'), ('UTC-01:00', 'UTC−01:00 — Azores'), ('UTC+00:00', 'UTC — United Kingdom, Portugal'), ('UTC+01:00', 'UTC+1 — Central Europe (CET)'), ('UTC+02:00', 'UTC+2 — Eastern Europe, South Africa'), ('UTC+03:00', 'UTC+3 — Moscow, East Africa'), ('UTC+04:00', 'UTC+4 — UAE, Armenia'), ('UTC+05:00', 'UTC+5 — Pakistan, Uzbekistan'), ('UTC+06:00', 'UTC+6 — Bangladesh, Kazakhstan'), ('UTC+07:00', 'UTC+7 — Thailand, Vietnam'), ('UTC+08:00', 'UTC+8 — China, Malaysia, Singapore'), ('UTC+09:00', 'UTC+9 — Japan, Korea'), ('UTC+10:00', 'UTC+10 — Australia (East)'), ('UTC+11:00', 'UTC+11 — Solomon Islands'), ('UTC+12:00', 'UTC+12 — New Zealand')], max_length=30)),
                ('role', models.CharField(choices=[('freelancer', 'Freelancer'), ('client', 'Client')], max_length=30, null=True)),
                ('is_custom', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_agency', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='MagicToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
