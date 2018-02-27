from django.contrib.auth.decorators import login_required,permission_required,user_passes_test

def is_superuser(u):
	return is_superuser

def is_doctor(u):
    return u.is_doctor

def is_staff_user(u):
    return u.is_staff