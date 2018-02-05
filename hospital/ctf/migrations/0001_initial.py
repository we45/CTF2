# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', unique=True, max_length=30, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, null=True, verbose_name='last name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_doctor', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='doctor status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plan_type', models.CharField(max_length=200)),
                ('datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('reason', models.TextField(null=True, blank=True)),
                ('token', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qualification', models.CharField(max_length=200)),
                ('gender', models.CharField(max_length=6, choices=[(b'', b'Select Gender'), (b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')])),
                ('specialization', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=12)),
                ('photo', models.ImageField(upload_to=b'doctors')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HealthPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('price', models.CharField(max_length=10)),
                ('doctor', models.ManyToManyField(to='ctf.Doctor')),
            ],
        ),
        migrations.CreateModel(
            name='HealthRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report', models.FileField(null=True, upload_to=b'reports', blank=True)),
                ('remarks', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LabTechnician',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('doctor', models.ManyToManyField(to='ctf.Doctor')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=12)),
                ('dob', models.DateField(default=datetime.date.today)),
                ('gender', models.CharField(max_length=6, choices=[(b'', b'Select Gender'), (b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')])),
                ('address', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ConsultantAppointment',
            fields=[
                ('appointment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ctf.Appointment')),
                ('doctor', models.ForeignKey(to='ctf.Doctor')),
            ],
            bases=('ctf.appointment',),
        ),
        migrations.CreateModel(
            name='HealthPlanAppointment',
            fields=[
                ('appointment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ctf.Appointment')),
            ],
            bases=('ctf.appointment',),
        ),
        migrations.AddField(
            model_name='healthrecord',
            name='patient',
            field=models.ForeignKey(to='ctf.Patient'),
        ),
        migrations.AddField(
            model_name='healthrecord',
            name='staff',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='healthplan',
            name='tests',
            field=models.ManyToManyField(to='ctf.Test'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(related_name='patient_appoinments', to='ctf.Patient'),
        ),
        migrations.AddField(
            model_name='healthplanappointment',
            name='plan',
            field=models.ForeignKey(related_name='patient_health_plans', to='ctf.HealthPlan'),
        ),
    ]
