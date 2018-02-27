from django.forms import ModelForm,Form
from django import forms
from django.utils.translation import ugettext_lazy as _
import sys
from ctf.models import *
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import authenticate

class PatientForm(ModelForm):
    name = forms.CharField(label='Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}))
    email = forms.EmailField(label='Email',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    phone = forms.CharField(label='Contact Number',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone Number'}))
    dob = forms.DateField(label='DOB',widget=forms.TextInput(attrs={'type':'date','class':'form-control','placeholder':'Date Of Birth'}))
    gender = forms.ChoiceField(label='Gender',choices=gender_choices,widget=forms.Select(attrs={'class':'form-control'}))
    address = forms.CharField(label='Address',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Address','cols':'65','rows':'4'}))

    class Meta:
        model = Patient
        fields = '__all__'

class AppointmentForm(ModelForm):
    plan_type = forms.ChoiceField(label='Appointment Type',choices=[('','Select Plan Type'),('Consultant','ConsultantAppointment'),('HealthPlan','HealthPlanAppointment')],widget=forms.Select(attrs={'class':'form-control'}))
    # datetime = forms.DateTimeField(input_formats = ("%Y/%m/%d %h:%i",),widget=forms.DateInput(format='%Y/%m/%d %h:%i',attrs={'id':'datetimepicker','class':'form-control'}))
    datetime = forms.CharField(widget=forms.TextInput(attrs={'type':'date','class':'form-control','placeholder':'Appointment Date'}))
    reason = forms.CharField(label='Reason',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Reason','cols':'65','rows':'4'}))

    class Meta:
        model = Appointment
        exclude = ('token','patient',)

class HealthPlanAppointmentForm(ModelForm):
    plan = forms.ModelChoiceField(queryset=HealthPlan.objects.all() ,label='HealthPlan',widget = forms.Select(attrs={'class':'form-control'}),required = False)

    class Meta:
        model = HealthPlanAppointment
        fields = ('plan',)

class ConsultantAppointmentForm(ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all() ,label='Doctor',widget = forms.Select(attrs={'class':'form-control'}),required = False)

    class Meta:
        model = ConsultantAppointment
        fields = ('doctor',)

class HealthRecordForm(ModelForm):
    report = forms.FileField(label='Report',widget=forms.ClearableFileInput(attrs={'class':'form-control'}))
    remarks = forms.CharField(label='Reason',widget=forms.Textarea(attrs={'class':'form-control'}))
    patient = forms.ModelChoiceField(queryset=Patient.objects.all() ,label='Patient',widget = forms.Select(attrs={'class':'form-control'}),required = True,)

    class Meta:
        model = HealthRecord
        exclude = ('staff',)

class HealthPlanForm(ModelForm):
    name = forms.CharField(label='Plan Name',widget=forms.TextInput(attrs={'class':'form-control'}))
    price = forms.CharField(label='Price',widget=forms.TextInput(attrs={'class':'form-control'}))
    tests = forms.ModelMultipleChoiceField(queryset=Test.objects.all() ,label='Tests',widget = FilteredSelectMultiple("Tests",is_stacked=False,attrs={'class':'form-control','multiple':True, }),required = True,)
    doctor = forms.ModelMultipleChoiceField(queryset=Doctor.objects.all() ,label='Doctor',widget = FilteredSelectMultiple("Doctor",is_stacked=False,attrs={'class':'form-control','multiple':True, }),required = True,)

    class Meta:
        model = HealthPlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(HealthPlanForm, self).__init__(*args, **kwargs)        
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['tests'].widget.attrs['class'] = 'form-control'
        self.fields['doctor'].widget.attrs['class'] = 'form-control'
          
class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'old_password_incorrect': _("Old Password didn't verify properly")
    }
    # old_password = forms.CharField(label=_("Old password"),
    #                                 widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Old Password'}))
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'New Password'}))
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        # old_password = self.cleaned_data.get('old_password')
        # user = authenticate(username=self.user.email, password=old_password)
        # if user is not None:
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2
        # else:
        #     raise forms.ValidationError(self.error_messages['old_password_incorrect'],code='old_password_incorrect')

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class ResendForm(forms.Form):
    uname = forms.CharField(required=False, label='Enter Username',widget=forms.TextInput(attrs={'autocomplete':'off','class':'form-control','placeholder':'Username'}))
    email = forms.EmailField(required=False, label='Enter Email',widget=forms.TextInput(attrs={'autocomplete':'off','class':'form-control','placeholder':'Email address'}),help_text='A valid email address, please.')

    def clean_uname(self):
        cleaned_data = super(ResendForm,self).clean()
        uname = cleaned_data.get("uname")
        if uname:
            usr = User.objects.filter(username=uname)
            if not usr:
                raise forms.ValidationError(" Username does not exist")                     
        return uname

    def clean_email(self):
        cleaned_data = super(ResendForm,self).clean()
        email = cleaned_data.get("email")
        if email:
            usr = User.objects.filter(email=email)
            if not usr:
                raise forms.ValidationError("Email-id does not exist")                      
        return email

    def clean(self):
        cleaned_data = super(ResendForm,self).clean()
        uname = cleaned_data.get("uname")
        email = cleaned_data.get("email")
        if not email and not uname:
            if email is not None and uname is not None:
                raise forms.ValidationError("Please enter email-id")                      
        return cleaned_data

class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. "
                                "Please enter it again."),
    })

class UserForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs=dict({'placeholder': 'First Name','class':'form-control'},required=True, max_length=30)))
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs=dict({'placeholder': 'Last Name','class':'form-control'},required=True, max_length=30)))
    email = forms.EmailField(label='Email',widget=forms.TextInput(attrs=dict({'placeholder': 'Email','class':'form-control','autocomplete':'off'},required=True, max_length=30)))   

    class Meta:
        model = User
        fields = ['first_name','last_name','email']

class CreateDoctorForm(UserForm):     
    qualification = forms.CharField(label='Qualification',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Qualification'}))
    gender = forms.ChoiceField(label='Gender',choices=gender_choices,widget=forms.Select(attrs={'class':'form-control'}))
    specialization = forms.CharField(label='Specialization',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Specialization'}))
    phone = forms.CharField(label='Contact Number',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Contact Number'}))
    photo = forms.ImageField(label='Profile Picture',widget=forms.ClearableFileInput(attrs={'class':'form-control'}))

class LabTechnicianForm(UserForm):
    doctor = forms.ModelMultipleChoiceField(queryset=Doctor.objects.all() ,label='Doctor',widget = FilteredSelectMultiple("Doctor",is_stacked=False,attrs={'class':'form-control','multiple':True, }),required = True,)


class TestForm(forms.ModelForm):
    name = forms.CharField(label='Test Name',widget=forms.TextInput(attrs=dict({'placeholder': 'Test Name','class':'form-control'},required=True, max_length=30)))

    class Meta:
        model = Test
        fields = '__all__'

class Secure_hashingform(forms.Form):
    hashing = forms.CharField(widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Hash Value','autocomplete':'off'}))

class Craking_hashingform(forms.Form):
    hashing = forms.CharField(widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Value','autocomplete':'off'}))
       

class patients_xss_form(forms.Form):
    search = forms.CharField(widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Search.........'}))
       

     
