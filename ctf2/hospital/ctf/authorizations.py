from tastypie.authorization import Authorization,DjangoAuthorization
from tastypie.exceptions import Unauthorized
import hmac as Myhmac
import hashlib
from tastypie.exceptions import ImmediateHttpResponse,BadRequest
from tastypie.http import HttpGone,HttpAccepted,HttpCreated,HttpBadRequest,HttpForbidden,HttpNotFound,HttpApplicationError,HttpUnauthorized,HttpResponse
from ctf.models import User,ConsultantAppointment, Appointment, Patient
from django.core.exceptions import ObjectDoesNotExist
#from _operator import _compare_digest as compare_digest
from django.utils.crypto import constant_time_compare as compare_digest
from tastypie.serializers import Serializer

class BaseAuthorization(Authorization):
    def read_detail(self, object_list, bundle):        
        return self.authorize_user(bundle)

    def create_list(self, object_list, bundle):
        raise Unauthorized('Creation not allowed through API')

    def create_detail(self, object_list, bundle):
        raise Unauthorized('Creation not allowed through API')

    def update_list(self, object_list, bundle):
        raise Unauthorized('Updation not allowed through API')

    def update_detail(self, object_list, bundle):
        raise Unauthorized('Updation not allowed through API')

    def delete_list(self, object_list, bundle):
        raise Unauthorized('Deletion not allowed through API')

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('Deletion not allowed through API')

class SuperUserAuthorization(BaseAuthorization):
    def authorize_user(self, bundle):
        if bundle.request.user.is_superuser:
            return True
        else:
            return False

    def read_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return object_list.all()
        else:
            raise Unauthorized('Forbidden')

class DoctorAuthorization(BaseAuthorization):
    def authorize_user(self, bundle):
        if bundle.request.user.is_doctor:
            return True
        else:
            return False

    def read_list(self, object_list, bundle):
        # print object_list
        if bundle.request.user.is_doctor:
            return object_list.filter(doctor__user=bundle.request.user)
        else:
            raise Unauthorized('Forbidden')

class DoctorAuthorization2(BaseAuthorization):

    def authorize_user(self, bundle):
        if bundle.request.user.is_doctor:
            return True
        else:
            return False

    def read_list(self, object_list, bundle):      
        if bundle.request.user.is_doctor:
            apppointment = ConsultantAppointment.objects.filter(doctor__user=bundle.request.user,patient__id__in=object_list.values_list('id', flat=True))
            # doctor = Doctor.objects.filter()
            # print apppointment
            return object_list.filter(id__in=apppointment)
        else:
            raise Unauthorized('Forbidden')

    def update_detail(self, object_list, bundle):
        if bundle.request.user.is_doctor:
            pid = bundle.data['id']
            name = bundle.data['name']
            email = bundle.data['email']
            gender = bundle.data['gender']
            dob = bundle.data['dob']
            phone = bundle.data['phone']
            try:
                if (pid and name and email and gender and dob and phone) != '':
                    Patient.objects.filter(id=pid).update(name=name,email=email,gender=gender,dob=dob,phone=phone)
                else:
                    return False
            except Exception as e:
                print e
            return True
        else:
            return False

class PatientAuthorization(BaseAuthorization):
    def authorize_user(self, bundle):
        if bundle.request.user.is_patient:
            return True
        else:
            return False

    def read_list(self, object_list, bundle):
        if bundle.request.user.is_patient:
            return object_list.all()
        else:
            raise Unauthorized('Forbidden')

class StaffAuthorization(BaseAuthorization):
    def authorize_user(self, bundle):
        if bundle.request.user.is_staff:
            return True
        else:
            return False

    def read_list(self, object_list, bundle):
        if bundle.request.user.is_staff:
            return object_list.all()
        else:
            raise Unauthorized('Forbidden')

class UserAuthorization(SuperUserAuthorization):
    pass

def get_status(hmac_value):
    digest_value = Myhmac.new('CtfFlag','{}',hashlib.sha256).hexdigest()
    return compare_digest(bytes(digest_value),bytes(hmac_value))             

class HmacAuthorization(BaseAuthorization):
    def authorize_user(self, bundle):        
        if bundle.request.user.is_staff:            
            hmac_value = bundle.request.META.get('HTTP_HMAC')      
            if hmac_value:
                if get_status(hmac_value):
                    return True
                else:
                    raise ImmediateHttpResponse(response=HttpForbidden({'Hmac Did not validate properly :(':''}))
            else:
                raise ImmediateHttpResponse(response=HttpForbidden({'Please provide hmac value':''}))
        else:
            return False

    def read_list(self, object_list, bundle):
        if bundle.request.user.is_staff:
            hmac_value = bundle.request.META.get('HTTP_HMAC')
            if hmac_value:                             
                if get_status(hmac_value):
                    return object_list.all()
                else:
                    raise ImmediateHttpResponse(response=HttpForbidden({'Hmac Did not validate properly :(':''}))
            else:
                raise ImmediateHttpResponse(response=HttpForbidden({'Please provide hmac value':''}))
        else:
            raise Unauthorized('Forbidden')
