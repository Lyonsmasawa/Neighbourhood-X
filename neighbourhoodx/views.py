from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from .forms import CustomUserForm, AdministratorForm
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
            user.first_name = user.first_name.lower()
            user.last_name = user.last_name.lower()
            user.save()

            Administrator.objects.create(user = user)

            login(request, user) 
            return redirect(adminProfile)

        else:
            messages.error(request, 'please try again')
    else:
        form = CustomUserForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/login_register.html', context)

@login_required(login_url='login')
def adminProfile(request):
    user = request.user
    if request.method == 'POST':
        form = AdministratorForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        return redirect(setUpNeighbourhood)

    else:
        form = AdministratorForm()

    context = {'form': form, }
    return render(request, 'neighbourhoodx/admin_profile_form.html', context)

@login_required(login_url='login')
def setUpNeighbourhood(request):


    context = {}
    return render(request, 'neighbourhoodx/set_up_neighbourhood.html', context)

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