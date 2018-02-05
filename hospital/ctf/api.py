from ctf.models import *
from tastypie.resources import ModelResource,ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication,Authentication,SessionAuthentication
from tastypie.serializers import Serializer
from django.forms.models import model_to_dict
import base64
from django.conf import settings 
from django.utils.datastructures import SortedDict
from django.db.models import Q
from ctf.authorizations import *
from tastypie import fields


class PatientResource(ModelResource):
    class Meta:
        queryset = Patient.objects.all()
        allowed_methods = ['get','put']
        include_resource_uri = False
        resource_name = 'patient'
        authentication = BasicAuthentication()
        authorization = DoctorAuthorization2()
        serializer = Serializer(formats=['json'])
        

class AppoinmentResource(ModelResource):
    patient = fields.ForeignKey(PatientResource,'patient', full = True)    
    class Meta:
        queryset = ConsultantAppointment.objects.all()
        authentication = SessionAuthentication()
        authorization = DoctorAuthorization()
        resource_name = 'appointments'        
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        allowed_methods = ['get']        
        include_resource_uri = False
        excludes = ['datetime','plan_type','reason','token']
        serializer = Serializer(formats=['json'])

        # excludes = ['email','address','dob','gender','phone']
    # def dehydrate(self, bundle):
    #     '''
    #     To return only particular field 
    #         - return bundle.data['name'] 
    #     ''' 
    #     patient = Patient.objects.get(id=bundle.data['id'])       
    #     bundle.data['appointments'] = Appointment.objects.filter(patient=patient).values()
    #     return bundle
    # def update_in_place(self, request, original_bundle, new_data):        
    #     if set(new_data.keys()) - set(self._meta.allowed_update_fields):
    #         raise BadRequest(
    #             'Only update on %s allowed' % ', '.join(
    #                 self._meta.allowed_update_fields
    #             )
    #         )

    #     return super(PatientResource, self).update_in_place(
    #         request, original_bundle, new_data
    #     )



        

class HealthPlanResource(ModelResource):
    class Meta:
        queryset = HealthPlan.objects.all()        
        authentication = BasicAuthentication()
        # authentication = SessionAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        allowed_methods = ['get']
        resource_name = 'plans'        
        authorization = HmacAuthorization()
        serializer = Serializer(formats=['json'])


    def dehydrate(self, bundle):						
        bundle.data = {'success':'Hmac values validated'}
        return bundle
    


