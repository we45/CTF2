from django.conf.urls import patterns, include, url

from django.contrib import admin
from ctf.views import *

from django.conf.urls import patterns, include, url
from django.contrib import admin
from ctf.views import *
from ctf.password import ValidatingPasswordChangeForm, ValidatingSetPasswordForm
from django.contrib import admin
from ctf import models, views
from django.views.static import *
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required

from django.conf.urls import url
from django.views.generic.base import RedirectView
admin.autodiscover()
from django.db.models import get_models, get_app
# for model in get_models(get_app('ctf')):
# 	print model.__name__
from ctf.api import *
from tastypie.api import Api
from django.http import Http404
# from django.conf.urls import handler404,handler500

ctf2 = Api(api_name='CTF')
ctf2.register(PatientResource())
ctf2.register(AppoinmentResource())
ctf2.register(HealthPlanResource())

# handler404 = page_not_found

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hospital.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^user/password/reset/$','django.contrib.auth.views.password_reset',{'post_reset_redirect' : '/user/password/reset/done/'}, name="password_reset"),
    url(r'^user/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z=]+)-(?P<token>.+)/$','django.contrib.auth.views.password_reset_confirm', {'set_password_form':ValidatingSetPasswordForm,'post_reset_redirect' : '/user/password/done/','template_name':'user_registration/password_reset_confirm.html'}),
    url(r'^user/password/done/$','django.contrib.auth.views.password_reset_complete',{'template_name':'user_registration/password_reset_complete.html'}),
    url(r'^reset_password/$', resend_pwd),
    url(r'^reset_password/(?P<resend>[a-z]+)/$', resend_pwd),
    url(r'^password_change/$','ctf.auth_views.password_change',{'post_change_redirect' : '/','template_name':'user_registration/password_change.html'}, name="password_change"),
    url(r'^password_change_secure/$','ctf.auth_views.password_change_securely',{'post_change_redirect' : '/','template_name':'user_registration/password_change_secure.html'}, name="password_change"),
    # url(r'^password_change/$','django.contrib.auth.views.password_change',{'password_change_form': ValidatingPasswordChangeForm,'post_change_redirect' : '/','template_name':'registration/password_change.html'}, name="password_change"),
    # url(r'^test/$', test),
    url(r'^xml_test/$', xml_test),


    url(r'^error/$', error),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', login_user),    
    url(r'^logout/', logout_user), 

    url(r'^doctors/', DoctorView.as_view()),
    url(r'^doctor/add/', create_doctor),
    url(r'^doctor/delete/(?P<pk>\d+)/$', DoctorDelete.as_view()),

    url(r'^tests/', list_tests),
    url(r'^secure_tests/', list_tests_securely),
    url(r'^test/add/', TestCreate.as_view()),
    url(r'^test/edit/(?P<pk>\d+)/$', TestUpdate.as_view()),
    url(r'^test/delete/(?P<pk>\d+)/$', TestDelete.as_view()),

    url(r'^technicians/', LabTechnicianView.as_view()),
    url(r'^technician/add/', create_technician),
    url(r'^technician/delete/(?P<pk>\d+)/$', LabTechnicianDelete.as_view()),
    
    url(r'^dashboard/', dashboard),    
    url(r'^$', home),
    url(r'^about/', home_about_us),
    # url(r'^appointment/', home_about_us),
    url(r'^contact_us/', home_contact_us),

    url(r'^api/', include(ctf2.urls)),
    # url(r'^users/', UsersView.as_view()),
    url(r'^user/delete/(?P<pk>\d+)/$', UserDelete.as_view()),

    url(r'^records/', HealthRecordView.as_view()),
    url(r'^record/add/', HealthRecordCreate.as_view()),
    url(r'^record/edit/(?P<pk>\d+)/$', HealthRecordUpdate.as_view()),
    url(r'^record/delete/(?P<pk>\d+)/$', HealthRecordDelete.as_view()),

    url(r'^plans/', HealthPlanView.as_view()),
    url(r'^plan/add/', HealthPlanCreate.as_view()),
    url(r'^plan/edit/(?P<pk>\d+)/$', HealthPlanUpdate.as_view()),
    url(r'^plan/delete/(?P<pk>\d+)/$', HealthPlanDelete.as_view()),
    # 
    url(r'^appointment/add/', create_appointment),
    url(r'^appointment/plan/', HealthPlanAppointmentView.as_view()),
    url(r'^appointment/doctor/', ConsultantAppointmentView.as_view()),
    
    # url(r'^testq/', testq),
    # url(r'^testa/$', testajax),
    url(r'^update/record/$', testajax),
    url(r'^publish/message/$', publish_msg),

    url(r'^patients/$', PatientsView.as_view()),
    url(r'^patient_list/$', patient_list),
    url(r'^secure/encoding/$', run_escaped_unescaped_attack),  
    url(r'^404/$', handler404),
    # url(r'^page_not_found/', page_not_found),
    url(r'^secure/hash/$', secure_hashing),
    url(r'^encrypt_modes/$', test_encryption_modes),
    url(r'^dep_analyzer/$', dep_analyzer),
    url(r'^http_response/$', list_error_pages),
)




if settings.DEBUG:
    handler404 = handler404
    urlpatterns += patterns('',(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),)
else:
    handler404 = handler404
    handler500 = handler500
    urlpatterns += patterns('',(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),)
    urlpatterns += patterns('',(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),)