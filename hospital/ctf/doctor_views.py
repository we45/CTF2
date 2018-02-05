from ctf.custom_views import *

class DoctorCreate(CreateView):
	template_name = 'create.html'
	model = Doctor
	context = {
		'patients' : Doctor.objects.all(),
		'form' : DoctorForm()
	}
	form_class = DoctorForm
	redirect_path = '/home/'

class DoctorUpdate(UpdateView):
	template_name = 'create.html'
	model = Doctor
	context = {
		'patients' : Doctor.objects.all(),
		'form' : DoctorForm()
	}
	form_class = DoctorForm
	redirect_path = '/home/'

