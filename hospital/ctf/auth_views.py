from django.shortcuts import render , render_to_response , get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash
)
from django.template.context import Context
from django.core.mail import send_mail
from django.template import RequestContext
from django.utils.http import int_to_base36, urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.template import loader
from django.template.context import Context
from django.core.mail import send_mail
from ctf.forms import *
from ctf import event_messages
from django.views.decorators.csrf import csrf_exempt


def user_send_mail(user, domain_override, email_template_name,use_https, token_generator,api_key):
	if not user.email:
		raise ValueError('Email address is required to send an email')
	if not domain_override:
		current_site = Site.objects.get_current()		
		site_name = current_site.name		
		domain = current_site.domain		
	else:
		site_name = domain = domain_override
	t = loader.get_template(email_template_name)
	c = {
		'email': user.email,
		'name':user.username,
		'domain': domain,
		'site_name': site_name,
		'uid': urlsafe_base64_encode(str(user.id)),
		'user': user,
		'token': token_generator.make_token(user),
		'protocol': use_https and 'https' or 'http',
        'api_key':api_key
	}
	send_mail(_("Your account for %s") % site_name,t.render(Context(c)), event_messages.default_email_address, [user.email])


@csrf_exempt
def password_change(request,
                    template_name='user_registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()           
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/dashboard/')
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': _('Password change'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

def password_change_securely(request,
                    template_name='user_registration/password_change_secure.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()           
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/dashboard/')
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': _('Password change'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)    


# send mail for resetting passwords
def resend_pwd(request, resend=None):
    '''
    This view is where, user can reset password by
    providing the username or email
    '''
    if request.method == "GET":
        if resend:
            if resend == "success":
                return render(request, 'user_registration/password_reset_success.html')
        resendform = ResendForm()
        return render(request, 'login/resend_passwd.html',{'resendform':resendform})
    if request.method == "POST":
        resendform = ResendForm(request.POST)
        if resendform.is_valid():
            email = resendform.cleaned_data['email']
            uname = resendform.cleaned_data['uname']
            if email:
                usr = User.objects.get(email=email)
            if uname:               
                usr = User.objects.get(username=uname)    
            user_send_mail(usr,domain_override=None,email_template_name='user_registration/password_reset_forgot_password.html',use_https=False, token_generator=default_token_generator,api_key='')
            return HttpResponseRedirect('/reset_password/success/')
        else:
            return render(request, 'login/resend_passwd.html',{'resendform':resendform})