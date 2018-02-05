from django.shortcuts import render,get_object_or_404
from django.views.generic import View,TemplateView
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import *
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from ctf.models import *
from django.views.generic.list import ListView as DjangoListView

class PermissionsRequiredMixin(object):
    """
    View mixin which verifies that the logged in user has the specified
    permissions.
    Settings:
    `required_permissions` - list/tuple of required permissions
    Example Usage:
        class SomeView(PermissionsRequiredMixin, ListView):
            ...
            required_permissions = (
                'app1.permission_a',
                'app2.permission_b',
            )
            ...
    """
    required_permissions = ()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        print request.user        
        if not request.user.has_perms(self.required_permissions):
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect('/login/')
        return super(PermissionsRequiredMixin, self).dispatch(
            request, *args, **kwargs)

class CustomListView(PermissionsRequiredMixin,DjangoListView):
    template_name = None
    model = None

class AbsoluteBaseView(PermissionsRequiredMixin,View):
	model = Model
	redirect_path = '/'
	required_permissions = ()
	model_name = Model.__class__.__name__

class BaseView(AbsoluteBaseView):
	template_name = '' 		 
	context = {}  
	form_class = None	

class CreateView(BaseView):
    def get(self,request):        
        return render(request,self.template_name,self.context)

    def post(self, request):        
        form = self.form_class(request.POST)         
        fields = {}
        if form.is_valid():            
            for name in form.fields:
            	fields[name] = form.cleaned_data[name]            	 
            m = self.model(**fields)         
            m.save()
            # log(user = request.user,action = "%s created %s"%(request.user.username,self.model_name),extra = {'%s'%self.model_name: str(form_save)})                               
            messages.success(request,'%s created successfully'%self.model_name)
            return HttpResponseRedirect(self.redirect_path)
        else:
            messages.warning(request,'Please correct the following errors')
            return render(request,self.template_name,self.context)

class UpdateView(BaseView):
	def get(self,request,pk):        
		obj = get_object_or_404(self.model,id=pk)
		form = self.form_class(instance=obj)
		self.context['form'] = form
		return render(request,self.template_name,self.context)

	def post(self, request,pk):
		obj = get_object_or_404(self.model,id=pk)
		form = self.form_class(request.POST,instance=obj)
		self.context['form'] = form         
		fields = {}
		if form.is_valid():            
			for name in form.fields:
				fields[name] = form.cleaned_data[name]			 
			obj.__dict__.update(fields)        
			obj.save()
			# log(user = request.user,action = "%s created %s"%(request.user.username,self.model_name),extra = {'%s'%self.model_name: str(form_save)})                               
			messages.success(request,'%s updated successfully'%self.model_name)
			return HttpResponseRedirect(self.redirect_path)
		else:
			messages.warning(request,'Please correct the following errors')
			return render(request,self.template_name,self.context)

class DeleteView(AbsoluteBaseView):
	def get(self,request,pk):        
		obj = get_object_or_404(self.model,id=pk)		
		obj.delete()
		messages.success(request,'%s deleted successfully'%self.model_name)
		return HttpResponseRedirect(self.redirect_path)