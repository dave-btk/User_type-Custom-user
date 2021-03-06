from django.shortcuts import render, HttpResponseRedirect, reverse, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser
import requests
import json


def google_captcha(clientkey):
    # ------- Google re-CAPTCHA code
    clientkey = clientkey
    secretkey = '6LcGnd0cAAAAADjQZAedMqJuQl044TUPxR8MRwbV'
    captcha_data = {
        'secret': secretkey,
        'response': clientkey
    }
    site_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_data)
    response = json.loads(site_response.text)
    verify = response['success']
    return verify


# Create your views here.
def login_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            fm = AuthenticationForm(request=request, data=request.POST)
            if fm.is_valid():
                uname = fm.cleaned_data['username']
                upass = fm.cleaned_data['password']
                user = authenticate(username=uname, password=upass)
                print(user.usertype, '----------------user-type')
                if user is not None:

                    # getting captcha response from html page
                    clientkey = request.POST.get('g-recaptcha-response')
                    # calling captcha method and sending response to it
                    verify = google_captcha(clientkey)
                    print('captcha value: ', verify)

                    if verify:
                        login(request, user)
                        if user.usertype == 1:
                            print("TYPE 1")
                            messages.success(request, 'Logged in successfully')
                            return HttpResponseRedirect(reverse('homepage'))
                        elif user.usertype == 2:
                            print("TYPE 2")
                            messages.success(request, 'Logged in successfully')
                            return HttpResponseRedirect(reverse('homepage'))
                        else:
                            print("login failed")
                            messages.error(request, 'Log-in failed')
                            return redirect('login_User')
                    else:
                        print("login failed")
                        messages.error(request, 'Log-in failed, attempt recaptcha')
                        return redirect('login_User')
        else:
            fm = AuthenticationForm()
            context = {
                "fm": fm
            }
        return render(request, 'loginpage.html', context)
    else:
        print("USER ALREADY LOGGED-IN")
        return HttpResponseRedirect(reverse('homepage'))


def homepage(request):
    if request.user.is_authenticated:
        print(request.user)
        print(request.user.usertype)
        if request.user.usertype == 1:
            data = "WELCOME CUSTOMER"
            context = {
                "data": data,
            }
        elif request.user.usertype == 2:
            data = "WELCOME SELLER"
            context = {
                "data": data,
            }
        return render(request, 'homepage.html', context)
    else:
        print("LOGIN FIRST!")
        return redirect('login_User')


def logout_user(request):
    logout(request)
    print("logged out")
    messages.success(request, "User Logged OUT")
    return redirect('login_User')


def orders_view(request):
    if request.user.is_authenticated:
        if request.user.usertype == 1:
            return render(request, 'orders.html')
        else:
            return redirect('page_not_found')
    else:
        print("LOGIN FIRST!")
        return redirect('login_User')


def sales_view(request):
    if request.user.is_authenticated:
        if request.user.usertype == 2:
            return render(request, 'sales.html')
        else:
            return redirect('page_not_found')
    else:
        print("LOGIN FIRST!")
        return redirect('login_User')


def page_not_found(request):
    return render(request, 'page_not_found.html')


def signup_users(request):
    if request.method == "POST":

        # getting captcha response from html page
        clientkey = request.POST.get('g-recaptcha-response')
        # calling captcha method and sending response to it
        verify = google_captcha(clientkey)
        print('captcha value: ', verify)

        if verify:
            email = request.POST.get('email')
            usertype = request.POST.get('usertype')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            print(email, usertype, password1, password2)
            if password1 == password2:
                usr_crt = CustomUser.objects.create_user(email=email, usertype=usertype, password=password1)
                usr_crt.save()
                print("SUCCESS!!")
                messages.success(request, "User Created")
                return redirect('login_User')
            else:
                messages.error(request, "WARNING!!! PASSWORDS SHOULD BE SAME")
                return redirect('create_user')
            # fm = CustomUserCreationForm(request.POST)
            # if fm.is_valid():
            #     fm.save()
            #     print("SUCCESS!!")
            #     return redirect('login_User')
            # else:
            #     print("Form submission failed")
            #     messages.error(request, 'Submission failed')
            #     return redirect('create_user')
        else:
            print("Form submission failed")
            messages.error(request, 'Log-in failed, attempt recaptcha')
            return redirect('create_user')
    else:
        form = CustomUserCreationForm()
        context = {
            "fm": form
        }
    return render(request, 'createuser.html', context)
