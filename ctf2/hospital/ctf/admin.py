from django.contrib import admin
from ctf.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(LabTechnician)
admin.site.register(Test)
admin.site.register(HealthPlan)
admin.site.register(HealthRecord)
admin.site.register(Appointment)
admin.site.register(HealthPlanAppointment)
admin.site.register(ConsultantAppointment)