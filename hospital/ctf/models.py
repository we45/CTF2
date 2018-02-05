from django.db import models
from django.db.models import Model,CharField,TextField,EmailField,DateField,ImageField,\
ManyToManyField,ForeignKey, FileField, DateTimeField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from django.db.models import get_model
import hashlib
import sha
import datetime

# Create your models here.
class UserManager(BaseUserManager):
	def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
		now = timezone.now()
		if not username:
			raise ValueError(_('The given username must be set'))
		email = self.normalize_email(email)
		user = self.model(username=username, email=email,
			is_staff=is_staff, is_active=True,
			is_superuser=is_superuser, last_login=now,
			created_on=now, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email=None, password=None, **extra_fields):
		return self._create_user(username, email, password, False, False,**extra_fields)

	def create_superuser(self, username, email, password, **extra_fields):
		user=self._create_user(username, email, password, True, True,**extra_fields)
		user.is_active=True
		user.save(using=self._db)
		return user
		

class SiteProfileNotAvailable(Exception):
	pass

class User(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(_('username'), max_length=30, unique=True,
		help_text=_('Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters'))
	first_name = models.CharField(_('first name'), max_length=30, blank=True, null=True)
	last_name = models.CharField(_('last name'), max_length=30, blank=True, null=True)
	email = models.EmailField(_('email address'),unique=True, max_length=255)
	is_staff = models.BooleanField(_('staff status'), default=False,
		help_text=_('Designates whether the user can log into this admin site.'))
	is_doctor = models.BooleanField(_('doctor status'), default=False,
		help_text=_('Designates whether the user can log into this admin site.'))
	# is_patient = models.BooleanField(_('patient status'), default=False,
	# 	help_text=_('Designates whether the user can log into this admin site.'))
	is_active = models.BooleanField(_('active'), default=True,
		help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
	created_on = models.DateTimeField(_('date joined'), default=timezone.now)	
	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username',]

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')

	def get_full_name(self):
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		return self.first_name

# ===================================================================
gender_choices = [('','Select Gender'),('M','Male'),('F','Female'),('O','Other')]

class Patient(Model):
	name = CharField(max_length=200)
	email = EmailField()
	phone = CharField(max_length=12)
	dob = DateField(default=datetime.date.today)
	gender = CharField(max_length=6,choices=gender_choices)
	address = TextField(blank=True,null=True)

	def __unicode__(self):
		return self.name

class Doctor(Model):
	user = models.OneToOneField(User)
	qualification = CharField(max_length=200)
	gender = CharField(max_length=6,choices=gender_choices)
	specialization = CharField(max_length=50)
	phone = CharField(max_length=12)
	photo = ImageField(upload_to='doctors')

	def __unicode__(self):
		full_name = '%s %s' % (self.user.first_name, self.user.last_name)
		return full_name

class LabTechnician(Model):
	user = models.OneToOneField(User)
	doctor = ManyToManyField(Doctor)

	def __unicode__(self):
		full_name = '%s %s' % (self.user.first_name, self.user.last_name)
		return full_name

class Test(Model):
	name = CharField(max_length=200)

	def __unicode__(self):
		return self.name

class HealthPlan(Model):
	name = CharField(max_length=200)
	price = CharField(max_length=10) 
	tests = ManyToManyField(Test)
	doctor = ManyToManyField(Doctor)

	def __unicode__(self):
		return self.name

class Appointment(Model):	
	plan_type = CharField(max_length=200)
	patient = ForeignKey(Patient,related_name='patient_appoinments')
	datetime = DateTimeField(default=datetime.datetime.now)
	reason = TextField(blank=True,null=True)
	token = CharField(max_length=200)
	
	def __unicode__(self):
		return "%s - %s"%(self.patient.name,self.datetime)

class HealthPlanAppointment(Appointment):
	plan = ForeignKey(HealthPlan,related_name='patient_health_plans')

	def generate_token(self):
		osha = hashlib.sha1('flag')
		self.token = "%s$%s$%s$%s"%(self.datetime,hashlib.md5(str(self.plan.id)).hexdigest(),osha.hexdigest(),self.patient)
		self.save()	

class ConsultantAppointment(Appointment):
	doctor = ForeignKey(Doctor)

	def generate_token(self):
		osha = hashlib.sha1('flag')
		self.token = "%s$%s$%s$%s"%(self.datetime,hashlib.md5(str(self.doctor.id)).hexdigest(),osha.hexdigest(),self.patient)
		self.save()	

class HealthRecord(Model):
	patient = ForeignKey(Patient)
	report = FileField(upload_to='reports',blank=True,null=True)
	remarks = TextField(blank=True,null=True)
	staff 	= ForeignKey(User)

	def __unicode__(self):
		return self.report.name





