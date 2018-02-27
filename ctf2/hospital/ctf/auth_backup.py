from tastypie.authorization import Authorization,DjangoAuthorization
from tastypie.exceptions import Unauthorized
import hmac,hashlib
from tastypie.exceptions import ImmediateHttpResponse,BadRequest
from tastypie.http import HttpGone,HttpAccepted,HttpCreated,HttpBadRequest,HttpForbidden,HttpNotFound,HttpApplicationError,HttpUnauthorized,HttpResponse
from ctf.models import User,ConsultantAppointment

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
        # print bundle.request.user       
        if bundle.request.user.is_doctor:
            return ConsultantAppointment.objects.filter(doctor__user=bundle.request.user)
        else:
            raise Unauthorized('Forbidden')

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
    digest_value = hmac.new('CtfFlag','{}',hashlib.sha256).hexdigest()
    return hmac.compare_digest(bytes(digest_value),bytes(hmac_value))             

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