from django.shortcuts import render
from django.shortcuts import render, get_object_or_404,redirect,reverse
from django.contrib.auth import authenticate,login,logout
from .forms import *
from django.views.generic.base import View
from django.contrib.auth.forms import *
from .models import *
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from enum import Enum
# Create your views here

class MessageType(Enum):
    danger = 1
    warning = 2
    success = 3
    info = 4

def IndexView(request):
    template_name = 'fikir/homepage.html'
    return render(request, template_name, {})


def TimelineView(request):
    template_name = 'fikir/timeline.html'
    return render(request, template_name, {})

def ProfileView(request):
    template_name = 'fikir/profile.html'
    return render(request, template_name, {})

class LoginView(View):
    form_class = LoginForm
    template_name = "fikir/login.html"
    formVariables = {
    'form': form_class,
    'pagetitle':'Giriş',
    'formtitle':'Giriş',
    'buttontext' : 'Giriş',
    'messagetext':'',
    'messagetype':''}
    def get(self, request):
        self.formVariables["messagetype"] = ""
        self.formVariables["messagetext"] = ""
        return render(request, self.template_name, self.formVariables)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if not form.cleaned_data.get('remember_me'):
                        request.session.set_expiry(0)
                    login(request, user)
                    return redirect('fikir:IndexView')
            self.formVariables["messagetype"] = MessageType.warning.name
            self.formVariables["messagetext"] = "Kullanıcı Adı veya Parola Yanlış"
            return render(request, self.template_name, self.formVariables)
        
        self.formVariables["messagetext"] = "Değerler geçersiz"
        self.formVariables["messagetype"] = MessageType.warning.name
        return render(request, self.template_name, self.formVariables)

class UserFormView(View):
    form_class = UserForm
    template_name = "fikir/signup.html"
    formVariables = {'form': form_class(None),
    'pagetitle':'Üye Ol',
    'formtitle':'Fikirlerini Paylaşmak İçin Üye Ol',
    'buttontext' : "Üye Ol",
    'messagetext':'',
    'messagetype':''}
    def get(self, request):
            return render(request, self.template_name,self.formVariables)

    def post(self, request):
        form = self.form_class(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Kullanici oluşturma
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            # Kullanıcıya bağlı kullanıcı profili oluşturma
            userprofile = UserProfile()
            userEmail = form.cleaned_data['email']

            userprofile.Name            = form.cleaned_data['name']
            userprofile.Surname         = form.cleaned_data['surname']
            userprofile.PhoneNumber     = form.cleaned_data['phoneNumber']
            userprofile.Birthday        = form.cleaned_data['birthday']
            userprofile.Email           = userEmail
            userprofile.ProfilePhoto    = form.cleaned_data['profilePhoto']
            userprofile.UserT           = user
            userprofile.save()


            # Aktivasyon maili gönderme
            # current_site = get_current_site(request)
            # mail_subject = 'Activate your blog account.'
            # message = render_to_string('active_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token':account_activation_token.make_token(user),
            # })
            # to_email = userEmail
            # email = EmailMessage(
            #             mail_subject, message, to=[to_email]
            # )
            # email.send()
            print(form.errors)
            # Oluşturulan Kullanıcıyla giriş yapma
            user = authenticate(username = username,password= password)
            if  user is not None:
                if user.is_active:
                    login(request,user)
                    return redirect('fikir:IndexView')

        self.formVariables["messagetype"] = "danger"
        self.formVariables["messagetext"] = form.errors.values
        return render(request,self.template_name,self.formVariables)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return redirect('fikir:IndexView')
    else:
        return HttpResponse('Aktivasyon maili geçersiz')