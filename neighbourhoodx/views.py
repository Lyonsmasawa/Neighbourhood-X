from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from .forms import CustomUserForm
from django.contrib.auth.decorators import login_required
from .models import Administrator, Neighbourhood, SOCIAL_SERVICES, Member, Post, Business

# Create your views here.
def home(request):

    context = {}
    return HttpResponse("works")

def registerPage(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()

            Member.objects.create(user = user)

            login(request, user) 
            return redirect('home')

        else:
            messages.error(request, 'please try again')
    else:
        form = CustomUserForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/login_register.html', context) 

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or Password')

    context = {'page': page}
    return render(request, 'neighbourhoodx/login_register.html', context) 

def logoutUser(request):
    logout(request)
    return redirect('home')