from ctf.forms import *
from ctf.custom_views import *
from django.contrib.auth import authenticate
from django.shortcuts import render_to_response,redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.conf import settings
import sys, os
from ctf.auth_views import *
from ctf.decorators import *
from django.views.generic.edit import CreateView as DjangoCreateView
from django.views.generic.list import ListView as DjangoListView
from tastypie.models import ApiKey
import json
from django.contrib.auth.models import AnonymousUser
from django.http import Http404

import inspect
import re
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.module_loading import import_string
from django.utils.translation import LANGUAGE_SESSION_KEY

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.template import Template, Context,RequestContext,loader
from django.utils.safestring import mark_safe
import urllib
from lxml import etree


parser = etree.XMLParser(load_dtd = True, dtd_validation = False, resolve_entities = True, recover = True, no_network = False)

def xml_test(request):
	if request.method == 'GET':
		return render(request,'xml_test.html')
	elif request.method == 'POST':
		ufile = request.FILES.get('upload')
		tree = etree.parse(ufile, parser = parser)
		return render(request,'xml_test.html',{'products':tree.iter('Prod')})
		

# def page_not_found(request):
# 	try:
# 		# template = '''<html>
# 		# 	<head>
# 		# 		<title>Error</title>
# 		# 	</head>
# 		# 	<body>
# 		# 		<h1>Oops that page doesn't exist!!</h1>
# 		# 		<h3>
# 		# 		{% autoescape off %}{{ message }}{% endautoescape %}
# 		# 		</h3>
# 		# 	</body>
# 		# 	</html>
# 		# '''
# 		# t = Template(template)

# 		# c = RequestContext(request,{'message':request.path})
# 		# return HttpResponse(t.render(c))
# 		# 
# 		# return loader.render_to_string('temp.html', context_instance=c)
# 		template = '''<html>
# 			<head>
# 				<title>Error</title>
# 			</head>
# 			<body>
# 				<h1>Oops that page doesn't exist!!</h1>
# 				<h3>
# 				%s
# 				</h3>
# 			</body>
# 			</html>
# 		'''%request.path
# 		# return HttpResponse(template)
# 		return mark_safe(template)
# 	except BaseException as e:
# 		print e
# 		return HttpResponseRedirect('/error/')

def create_session(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if not request.session.exists(request.session.session_key):
            request.session.create()
        return function(request, *args, **kwargs)
    return decorator

def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)

    # remember language choice saved to session
    language = request.session.get(LANGUAGE_SESSION_KEY)

    # request.session.flush()
    request.session.create()

    if language is not None:
        request.session[LANGUAGE_SESSION_KEY] = language

    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'

def login(request, user):
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()
    # if SESSION_KEY in request.session:
    #     if _get_user_session_key(request) != user.pk or (session_auth_hash and request.session.get(HASH_SESSION_KEY) != session_auth_hash):
    #        # To avoid reusing another user's session, create a new, empty
    #        # session if the existing session corresponds to a different
    #        # authenticated user.
    #        print request.session
    #        # request.session.flush()
    # else:
    # request.session.cycle_key()
    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = user.backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
       request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


def is_superuser(user):
	return user.is_superuser

def login_user(request):
	try:
		if request.method=="POST":
			username = request.POST['email_id']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)					
					return HttpResponseRedirect('/dashboard/')
			else:
				messages.add_message(request, messages.ERROR, 'Invalid Username or Password')
				return render(request, 'login/login.html')		
		return render_to_response('login/login.html', context_instance=RequestContext(request))
	except Exception as e:
		print e


def logout_user(request):  
    logout(request)
    # request.session.flush()
    # request.user = AnonymousUser
    return HttpResponseRedirect('/login/')

def log_exception(user_name,e,view_path):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg = "Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)
    if settings.DEBUG:
        print msg
    else:
    	pass
        # send_error_email(user_name,'/celery/%s/'%view_path,msg) 

@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def create_doctor(request):
	try:		
		if request.method == "GET":
			form = CreateDoctorForm()
			# print request.user.username
			return render(request,'doctor/create.html',{'form':form})
		elif request.method == "POST":
			form = CreateDoctorForm(request.POST,request.FILES)
			if form.is_valid():
				form_save = form.save(commit=False)
				form_save.username = form.cleaned_data['email']
				form_save.is_doctor = True
				form_save.save()
				form_dict = {
					'qualification':form.cleaned_data['qualification'],
					'gender':form.cleaned_data['gender'],
					'specialization':form.cleaned_data['specialization'],
					'phone':form.cleaned_data['phone'],
					'photo':form.cleaned_data['photo'],
					'user':form_save
				}				
				d = Doctor.objects.create(**form_dict) 
				try:
					api_key = ApiKey.objects.get(user = form_save.id)                        
				except ObjectDoesNotExist:
					api_key = ApiKey.objects.create(user = form_save)
					api_key.save()				                     
				user_send_mail(form_save,domain_override=None,email_template_name='user_registration/password_reset_email_for_module_admin.html',use_https=False, token_generator=default_token_generator,api_key = api_key.key)
				return HttpResponseRedirect('/dashboard/')       
			else:				
				return render(request,'doctor/create.html',{'form':form})
		else:
			raise Http404	
	except Exception as e:
		log_exception(request.user,e,'doctor_create')
		raise Http404

@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def update_doctor(request,pk):
	try:
		obj = Doctor.objects.get(id=pk)		
		if request.method == "GET":
			form = CreateDoctorForm(instance=obj)
			return render(request,'doctor/create.html',{'form':form})
		elif request.method == "POST":
			form = CreateDoctorForm(request.POST,request.FILES)
			if form.is_valid():
				form_save = form.save(commit=False)
				form_save.username = form.cleaned_data['email']
				form_save.is_doctor = True
				form_save.save()
				form_dict = {
					'qualification':form.cleaned_data['qualification'],
					'gender':form.cleaned_data['gender'],
					'specialization':form.cleaned_data['specialization'],
					'phone':form.cleaned_data['phone'],
					'photo':form.cleaned_data['photo'],
					'user':form_save
				}				
				d = Doctor.objects.create(**form_dict)				
				return HttpResponseRedirect('/doctors/')       
			else:				
				return render(request,'doctor/create.html',{'form':form})
		else:
			raise Http404	
	except Exception as e:
		log_exception(request.user,e,'doctor_create')
		raise Http404

class DoctorView(DjangoListView):
	template_name = 'doctor/doctors.html'
	model = Doctor
	def get_queryset(self):
		if self.request.user.is_superuser:
			return Doctor.objects.all()		
		else:
			raise Http404

class DoctorDelete(DeleteView):	
	model = User	
	redirect_path = '/doctors/'
	def get_queryset(self):
		if self.request.user.is_superuser:
			return Doctor.objects.all()		
		else:
			raise Http404

class LabTechnicianView(DjangoListView):
	template_name = 'technician/technicians.html'
	model = LabTechnician

	def get_queryset(self):
		if self.request.user.is_superuser:
			return LabTechnician.objects.all()
		elif self.request.user.is_doctor:			
			return LabTechnician.objects.filter(doctor__user=self.request.user)		
		else:
			raise Http404

class LabTechnicianDelete(DeleteView):	
	model = User	
	redirect_path = '/technicians/'
	def get_queryset(self):
		if self.request.user.is_superuser:
			return LabTechnician.objects.all()		
		else:
			raise Http404

from django.utils.html import escape
@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def create_technician(request):
	try:		
		if request.method == "GET":
			form = LabTechnicianForm()
			return render(request,'technician/create.html',{'form':form})
		elif request.method == "POST":
			form = LabTechnicianForm(request.POST)
			if form.is_valid():
				form_save = form.save(commit=False)
				username = form.cleaned_data['email']
				form_save.username = username
				form_save.is_staff = True
				form_save.save()		
				doctors = form.cleaned_data['doctor']						
				technician = LabTechnician.objects.create(user=form_save) 
				for d in doctors:
					technician.doctor.add(d)
				try:
					api_key = ApiKey.objects.get(user = form_save.id)                        
				except ObjectDoesNotExist:
					api_key = ApiKey.objects.create(user = form_save)
					api_key.save()
				user_send_mail(form_save,domain_override=None,email_template_name='user_registration/password_reset_email_for_module_admin.html',use_https=False, token_generator=default_token_generator,api_key = api_key.key)
				return HttpResponseRedirect('/technicians/')       
			else:				
				return render(request,'technician/create.html',{'form':form})
		else:
			raise Http404	
	except Exception as e:
		log_exception(request.user,e,'doctor_create')
		raise Http404

# class TestView(DjangoListView):
# 	template_name = 'test/tests.html'
# 	model = Test
@login_required(login_url='/login/')
def list_tests(request):
	try:		
		if request.method == "GET":
			tests = Test.objects.all()
			return render(request,'test/tests.html',{'tests':tests})
		elif request.method == "POST":
			search = request.POST.get('search')
			# qry = "SELECT PName,PPrice,img,id,PSName_id FROM cwasp.app_wanted_product where PName = '%s'"%(search)
			# ' or '1' = '1
			qry = "SELECT id,name FROM public.ctf_test where name = '%s'"%(search)
			# search = "%%%s%%"%search
			# qry = "SELECT * FROM public.ctf_test where name like '%s'"%(search)
			# print "qry-->",qry
			tests = Test.objects.raw('%s'%qry)
			abc = "hiiiiiiiii"
			return render(request,'test/tests.html',{'tests':tests,'abc':abc})
		else:
			raise Http404	
	except Exception as e:
		# print "Exception-->",e
		# log_exception(request.user,e,'doctor_create')
		raise Http404(e.message)


@login_required(login_url='/login/')
def list_tests_securely(request):
	try:		
		if request.method == "GET":
			tests = Test.objects.all()
			return render(request,'test/tests.html',{'tests':tests})
		elif request.method == "POST":
			search = request.POST.get('search')
			tests = Test.objects.filter(name__contains=search)
			return render(request,'test/tests.html',{'tests':tests})
		else:
			raise Http404	
	except Exception as e:
		# print "Exception-->",e
		# log_exception(request.user,e,'doctor_create')
		raise Http404(e.message)

class TestCreate(CreateView):
	template_name = 'test/create.html'
	model = Test
	context = {		
		'form' : TestForm()
	}
	form_class = TestForm
	redirect_path = '/tests/'

class TestUpdate(UpdateView):
	template_name = 'test/create.html'
	model = Test
	context = {		
		'form' : TestForm()
	}
	form_class = TestForm
	redirect_path = '/tests/'

class TestDelete(DeleteView):	
	model = Test	
	redirect_path = '/tests/'


class UsersView(TemplateView):
	template_name = 'users.html'
from django.utils.safestring import mark_safe
class PatientsView(TemplateView):
	form_class = patients_xss_form
	template_name = 'patient/patients.html'
	def get(self, request, *args, **kwargs):
		form = self.form_class()		
		xss_reflected = request.GET.get('search')
		if xss_reflected:
			val = xss_reflected			
			response = render_to_response(self.template_name, {'form': form,'val':val},context_instance=RequestContext(request))
			response['X-XSS-Protection'] = 0			
			return response
		else:
			return render(request, self.template_name, {'form': form})



class UserDelete(DeleteView):	
	model = User	
	redirect_path = '/users/'


class HealthPlanCreate(DjangoCreateView):
	template_name = 'plan/createplan.html'
	model = HealthPlan
	context = {
		'form' : HealthPlanForm()
	}
	form_class = HealthPlanForm
	success_url = '/dashboard/'

class HealthPlanUpdate(UpdateView):
	template_name = 'plan/createplan.html'
	model = HealthPlan
	context = {
		'form' : HealthPlanForm()
	}
	form_class = HealthPlanForm
	redirect_path = '/dashboard/'

class HealthPlanDelete(DeleteView):	
	model = HealthPlan	
	redirect_path = '/dashboard/'

class HealthPlanView(DjangoListView):
	template_name = 'plan/plans.html'
	model = HealthPlan

class HealthRecordCreate(DjangoCreateView):
	template_name = 'record/createrecord.html'
	model = HealthRecord
	form_class = HealthRecordForm
	success_url = '/dashboard/'
	def get_queryset(self):
		if self.request.user.is_superuser:
			return HealthRecord.objects.all()		
		elif self.request.user.is_staff:			
			return HealthRecord.objects.filter(staff=self.request.user)
		else:
			raise Http404

	def form_valid(self, form):
		data = form.save(commit=False)
		data.staff = self.request.user
		data.save()
		return super(HealthRecordCreate, self).form_valid(form)


class HealthRecordUpdate(UpdateView):
	template_name = 'record/recordcreate.html'
	model = HealthRecord
	context = {
		'form' : HealthRecordForm()
	}
	form_class = HealthRecordForm
	redirect_path = '/dashboard/'

class HealthRecordDelete(DeleteView):	
	model = HealthRecord	
	redirect_path = '/dashboard/'

class HealthRecordView(DjangoListView):
	template_name = 'record/records.html'
	model = HealthRecord

	def get_queryset(self):
		if self.request.user.is_superuser:
			return HealthRecord.objects.all()		
		elif self.request.user.is_staff:			
			return HealthRecord.objects.filter(staff=self.request.user)
		else:
			raise Http404

class ConsultantAppointmentView(DjangoListView):
	template_name = 'patient/docappointment.html'
	model = ConsultantAppointment

	def get_queryset(self):
		if self.request.user.is_superuser:
			return ConsultantAppointment.objects.all()
		elif self.request.user.is_doctor:			
			return ConsultantAppointment.objects.filter(doctor__user=self.request.user)
		else:
			raise Http404

class HealthPlanAppointmentView(DjangoListView):
	template_name = 'patient/planappointment.html'
	model = HealthPlanAppointment
	
	def get_queryset(self):
		if self.request.user.is_superuser:
			return HealthPlanAppointment.objects.all()
		elif self.request.user.is_doctor:			
			return HealthPlanAppointment.objects.filter(plan__doctor__user=self.request.user)
		else:
			raise Http404


class PatientDelete(DeleteView):	
	model = Patient	
	redirect_path = '/patients/'
	def get_queryset(self):
		if self.request.user.is_superuser:
			return Patient.objects.all()		
		else:
			raise Http404

def create_appointment(request):
	if request.method == "GET":
		appointmentform = AppointmentForm()
		planappointment = HealthPlanAppointmentForm()
		doctorappointment = ConsultantAppointmentForm()
		patientform = PatientForm()
		return render(request,'patient/createappointment.html', {'appointmentform':appointmentform,'patientform':patientform,'doctorappointment':doctorappointment,'planappointment':planappointment})
	if request.method == "POST":
		final_message  ={}
		appointmentform = AppointmentForm(request.POST)
		planappointment = HealthPlanAppointmentForm(request.POST)
		doctorappointment = ConsultantAppointmentForm(request.POST)
		patientform = PatientForm(request.POST)
		if appointmentform.is_valid() and patientform.is_valid():
			patient = patientform.save()
			appointment_type = appointmentform.cleaned_data['plan_type']
			if appointment_type == "Consultant":
				if doctorappointment.is_valid():
					docappointment = doctorappointment.save(commit=False)
					docappointment.patient = patient
					docappointment.datetime = appointmentform.cleaned_data['datetime']
					docappointment.plan_type = appointmentform.cleaned_data['plan_type']
					docappointment.reason = appointmentform.cleaned_data['reason']
					docappointment.doctor = doctorappointment.cleaned_data['doctor']
					docappointment.save()
					docappointment.generate_token()
					final_message['token'] = docappointment.token
					final_message['msg'] = "Thank You for booking the appointment."
					# return HttpResponse(json.dumps(final_message),content_type='application/json')
					return render(request,'patient/createappointment.html', {'appointmentform':appointmentform,'patientform':patientform,'doctorappointment':doctorappointment,'planappointment':planappointment,'final_message':final_message})
				else:
					return render(request,'patient/createappointment.html', {'appointmentform':appointmentform,'patientform':patientform,'doctorappointment':doctorappointment,'planappointment':planappointment})
			elif appointment_type == "HealthPlan":
				if planappointment.is_valid():
					plappointment = planappointment.save(commit=False)
					plappointment.patient = patient
					plappointment.datetime = appointmentform.cleaned_data['datetime']
					plappointment.plan_type = appointmentform.cleaned_data['plan_type']
					plappointment.reason = appointmentform.cleaned_data['reason']
					plappointment.plan = planappointment.cleaned_data['plan']
					plappointment.save()
					plappointment.generate_token()
					final_message['token'] = plappointment.token
					final_message['msg'] = "Thank You for booking the appointment."
					# return HttpResponse(json.dumps(final_message),content_type='application/json')
					# return render(request,'patient/createappointment.html', {'appointmentform':appointmentform,'patientform':patientform,'doctorappointment':doctorappointment,'planappointment':planappointment,'final_message':final_message})
				else:
					return render(request,'patient/createappointment.html', {'appointmentform':appointmentform,'patientform':patientform,'doctorappointment':doctorappointment,'planappointment':planappointment})
		else:
			# print "appooint-->",appointmentform.errors,"HealthPlan--->",planappointment.errors,"Doctor-->",doctorappointment.errors
			return render(request,'patient/createappointment.html', {'appointmentform':appointmentform,'patientform':patientform,'doctorappointment':doctorappointment,'planappointment':planappointment})

def home(request):
	return render(request,'home/home.html')


def home_about_us(request):
	return render(request,'home/about_us.html')


def home_contact_us(request):
	return render(request,'home/contact_us.html')

@login_required(login_url='/login/')
def dashboard(request):
	return render(request,'dashboard/dashboard.html')

@login_required(login_url='/login/')
def testq(request):
	if request.method == "GET":
		return render(request,'testq.html')
	elif request.method == "POST":
		search = request.POST.get('search')
		# qry = "SELECT PName,PPrice,img,id,PSName_id FROM cwasp.app_wanted_product where PName = '%s'"%(search)
		# ' or '1' = '1
		qry = "SELECT * FROM public.ctf_patient where name = '%s'"%(search)
		print "Qry",qry
		patients = Patient.objects.raw('%s'%qry)
		for pat in patients:
			print "patient",pat
		return render(request,'testq.html',{'patients':patients})

import base64
@login_required(login_url='/login/')
def testajax(request):
	if request.method == "POST":
		if request.is_ajax():
			try:
				rid = request.POST.get('rid',None)
				remarks = request.POST.get('remarks',None)
				if rid is not None and remarks is not None:
					try:
						healthrecord = HealthRecord.objects.get(id=rid)
						healthrecord.remarks = remarks
						healthrecord.save()
						msg = "Succesfully updated %s's Health Record."%healthrecord.patient
						print base64.b64encode(msg)
						return HttpResponse(msg)
					except HealthRecord.DoesNotExist:
						return HttpResponse('Please fill right Information',status=404)
				else:
					return HttpResponse('Please fill right Information',status=404)
			except Exception as e:
				print "Exception",e
				return HttpResponse('Please fill right Information',status=404)
				# print "EE-------------->",e
	elif request.method == "GET":
		return render(request, 'testajax.html')

import paho.mqtt.client as mqtt
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("$SYS/#")


@login_required(login_url='/login/')
def publish_msg(request):
	if request.method == "POST":
		msg = request.POST.get('msg', None)
		if msg is not None:
			# print "message",msg
			final_message = "You have found Flag - %s"%msg
			client = mqtt.Client()
			client.on_connect = on_connect
			client.connect("162.243.52.237", 1833, 60)
			client.publish("Medicine", final_message)
			client.disconnect()
			return HttpResponseRedirect('/publish/message/')
		else:
			raise Http404
	elif request.method == "GET":
		return render(request, 'publish.html')

import cgi
def run_escaped_unescaped_attack(request):
    xss_vector = request.POST.get('string', '')
    if request.method == 'POST' and 'escape' in request.POST:
        push_string = cgi.escape(xss_vector)
        return render(request, 'encoding.html', {'vector': push_string}) 
    if request.method == 'POST' and 'unescape' in request.POST:
        push_string = xss_vector
        return render(request, 'encoding.html', {'vector': push_string})
    if request.method == "GET":
        return render(request, 'encoding.html')
		
def error(request):
	return render(request,'error.html')

def handler404(request):
   return render(request, 'error.html')

def handler500(request):
   return render(request, 'error.html')


def patient_list(request):
	# print "Request Method -->",request.method
	if request.method == "GET":
		return render(request,'error.html')
	elif request.method == "HEAD":
		patients = Patient.objects.all().values()[:10]
		# json_data = json.dumps(patients)
		# print "json data ==>",patients
		response = HttpResponse()
		response["PatientData"] = patients
		return response
		
import hashlib
import uuid
import base64
import os
import binascii
def secure_hashing(request):
	'''
		In this function we are calling sha1 hashing methods.
	'''
	try:
		if request.method == "GET":
			form = Secure_hashingform()
			return render (request,'secure/hashing.html',{'form':form})
		elif request.method == "POST":
			form = Secure_hashingform(request.POST)
			if form.is_valid():
				hashing = form.cleaned_data['hashing']

				sha1_object = hashlib.sha1(hashing)
				sha1_det = sha1_object.hexdigest()

				sha1_salt = uuid.uuid4().hex
				sha1_with_salt = hashlib.sha1(hashing+sha1_salt).hexdigest()

				salt  = base64.urlsafe_b64encode(uuid.uuid4().bytes)
				t_sha = hashlib.sha1()
				t_sha.update(hashing+salt)
				sha1_with_salt2 =  base64.urlsafe_b64encode(t_sha.digest())

				salt4 = os.urandom(8)
				hash4 = hashlib.sha1(hashing + salt)
				sha1_with_salt3 = hash4.hexdigest()
			return render (request,'secure/hashing.html',{'form':form,'sha1_det':sha1_det,'sha1_with_salt':sha1_with_salt,'sha1_with_salt2':sha1_with_salt2,'sha1_with_salt3':sha1_with_salt3})
	except Exception, e:		
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print "Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)


from hospital.utils import TestEncyption
def test_encryption_modes(request):
	try:
		context = {}
		if request.method == 'GET':
			return render(request,'encryption_modes.html')
		elif request.method == 'POST':
			message = request.POST.get('message')
			t = TestEncyption()
			context['data'] = {
				'CBC':t.modes(message,mode='CBC'),
				'ECB':t.modes(message,mode='ECB'),
				'CFB':t.modes(message,mode='CFB'),
			}			
			return render(request,'encryption_modes.html',context)
	except:
		return HttpResponseRedirect('/')

from elasticsearch import Elasticsearch
def dep_analyzer(request):
	final_cves = []
	es = Elasticsearch([settings.ES_PATH], http_auth=('Sherlock', 'Watson'),)
	with open('all_requirements.txt','r') as reqfile:
	    for req in reqfile.readlines():
	        d = {}
	        str_req = req.split('==')[0].rstrip()
	        query = {
		      	"query": {
		        	"match_phrase": {
		          		"description": str_req		          
		        	}
		      	}
		    }	        
	        results = es.search(index = 'nvd', doc_type='cve', body = query)	        
	        d[str_req] = results['hits']['hits']
	        final_cves.append(d)
	return render(request,'cve.html', {'cves': final_cves})

import requests
from django.shortcuts import render_to_response
from django.template import RequestContext

def list_error_pages(request):
	'''
		In this funcrion we are calling 
		multiple http requests and responses.	
	'''
	try:
		if request.method == "GET":
			return render (request,'error/list_error_pages.html')		
		elif request.method == "POST":			
			# 200
			if '200' in request.POST:
				r = requests.get('http://localhost/about')			
				# print dir(r)
				r.status_code = 200
				request_name = 'Ok'
				response_code = r.status_code			
				response_header = r.headers
				req_headers =  r.request.headers
				# print type(req_headers)
			elif '301' in request.POST:
				# 301
				mv_permanently = requests.get('http://localhost/testing/')
				mv_permanently.status_code = 301
				request_name = "Moved Permanently"
				response_code= mv_permanently.status_code
				response_header = mv_permanently.headers	
				req_headers =  mv_permanently.request.headers
			elif '302' in request.POST:
				# 302
				found_cm_way = requests.get('http://localhost/testing/')
				found_cm_way.status_code = 302
				request_name = "Found"
				response_code= found_cm_way.status_code
				response_header = found_cm_way.headers
				req_headers =  found_cm_way.request.headers
			elif '401' in request.POST:
				# 401			
				unauth = requests.get('http://localhost/sdplans/abcasdsd')
				# print unauth.has_header
				unauth.status_code = 401
				request_name = 'Unauthorized'
				response_code = unauth.status_code
				response_header = unauth.headers
				req_headers =  unauth.request.headers
			elif '403' in request.POST:
				# 403
				for_bidden = requests.get('http://localhost/sdplans/abcasdsd')						
				for_bidden.status_code = 403
				request_name = "Forbidden"
				response_code = for_bidden.status_code
				response_header = for_bidden.headers
				req_headers =  for_bidden.request.headers
			elif '404' in request.POST:
				# 404
				not_found = requests.get('http://localhost/sdplans/abcasdsd')
				not_found.status_code = 404
				request_name = 'Not Found'
				response_code = not_found.status_code
				response_header = not_found.headers
				req_headers =  not_found.request.headers
			elif '500' in request.POST:
				# 500
				inter_server = requests.get('http://localhost/sdplans/abcasdsd')
				inter_server.status_code = 500
				request_name = 'Internal Server Error'
				response_code = inter_server.status_code
				response_header = inter_server.headers
				req_headers =  inter_server.request.headers
			elif '502' in request.POST:
				# 502
				bad_gateway = requests.get('http://localhost/sdplans/abcasdsd')
				bad_gateway.status_code = 502
				request_name = 'Bad Gateway'
				response_code = bad_gateway.status_code
				response_header = bad_gateway.headers
				req_headers =  bad_gateway.request.headers	
			return render(request,'error/list_error_pages.html',{'request_name':request_name,'response_code':response_code,'response_header':response_header,'req_headers':req_headers})
	except Exception as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print "Line no :%s Exception %s"%(exc_traceback.tb_lineno,e)

from lxml import etree
def parse_xml():
	es = Elasticsearch([settings.ES_PATH], http_auth=('Sherlock', 'Watson'))

	if not es.indices.exists(index = 'nvd'):
		es.indices.create(index = 'nvd')

	all_items = etree.parse('allitems.xml')

	root = all_items.getroot()
	all_my_items = root.findall('item')

	cve_object = {}
	for item in all_my_items:
		cve_object = {}
		cve_id = item.get('name')
		cve_object['name'] = cve_id
		description = item.findtext('desc')
		cve_object['description'] = description
		all_refs = item.find('refs')
		reflist = [ref.text for ref in all_refs]
		cve_object['references'] = reflist
		# print cve_object
		es.index(index='nvd', doc_type='cve', body = cve_object)
	print 'Data dumped to ES'
