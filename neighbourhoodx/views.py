import random
import string
from urllib import request
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User

from .emails import send_welcome_resident, send_welcome_email
from .forms import AddResidentForm, CustomUserForm, AdministratorForm, NeighbourhoodForm, PostForm, SocialServicesForm
from django.contrib.auth.decorators import login_required
from .models import Administrator, Neighbourhood, SOCIAL_SERVICES, Member, Post, Business, SocialServices
import folium

# Create your views here.
def home(request):

    context = {}
    return HttpResponse("works")


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

            try:
                email = user.email
                name = user.username
                send_welcome_email(name, email)

                login(request, user) 

            except:
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
    user = request.user
    administrator = Administrator.objects.get(user = user)

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood != None:
        return redirect(adminDashboard)

    else:
        if request.method == 'POST':
            form = NeighbourhoodForm(request.POST)
            if form.is_valid():
                neighbourhood = form.save(commit=False)
                neighbourhood.admin = administrator
                neighbourhood.save()
            return redirect(adminDashboard)

        else:
            form = NeighbourhoodForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/set_up_neighbourhood.html', context)

@login_required(login_url='login')
def adminDashboard(request):
    user = request.user
    administrator = Administrator.objects.get(user = user)

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood != None:
        n_long = get_neighbourhood.location[0]
        n_lat = get_neighbourhood.location[1]   
        social_services = SocialServices.objects.filter(neighbourhood = get_neighbourhood)

        # folium map
        m = folium.Map(location=[n_lat, n_long], zoom_start=16)

        #location marker
        folium.Marker([n_lat, n_long],
            popup=f'<strong>{get_neighbourhood.name}</strong> Neighbourhood',
            tooltip='Click here for more', 
            icon=folium.Icon(icon='home', color='blue')
            ).add_to(m)

        folium.CircleMarker(
            [n_lat, n_long],
            tooltip=f'<strong>{get_neighbourhood.name}</strong> Neighbourhood',
            popup='Join our neighbourhood', 
            radius = 300,
            ).add_to(m)

        if social_services != None:
            for service in social_services:
                s_long = service.location[0]
                s_lat = service.location[1]

                folium.Marker([s_lat, s_long],
                    popup=f'<strong>{service.name}</strong>',
                    tooltip='Click here for more', 
                    icon=folium.Icon(icon='cloud', color='red')
                    ).add_to(m),

        else:
            pass
    
    else:
        return redirect(setUpNeighbourhood)

    m = m._repr_html_() #html representation
    
    context = {'map': m, 'hood': get_neighbourhood}
    return render(request, 'neighbourhoodx/admin_dashboard.html', context)

@login_required(login_url='login')
def addResident(request):
    user = request.user

    administrator = Administrator.objects.get(user = user)

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        if request.method == 'POST':
            form = AddResidentForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']

                #generates random password for the resident
                password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

                # creates user with the given details
                resident_user = User.objects.create(username = username, email = email, password = password)

                #save as a member of the neighbourhood
                member = Member(user=resident_user, neighbourhood=get_neighbourhood)
                member.save()
                
                #increase the residents count
                members = Member.objects.filter(neighbourhood = get_neighbourhood)
                member_count = members.count()
                get_neighbourhood.occupants = member_count + 1
                get_neighbourhood.save()
                
                #send email to resident
                send_welcome_resident(name,username,password,administrator.user.username ,get_neighbourhood.name, email)
            
            return redirect(adminDashboard)

        else:
            form = AddResidentForm()
      
    context = {'form': form}
    return render(request, 'neighbourhoodx/add_resident.html', context)

def viewResidents(request):
    user = request.user
    administrator = Administrator.objects.get(user = user)
    get_neighbourhood = Neighbourhood.objects.get(admin = administrator)

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        #basic option
        # residents = Member.objects.filter(neighbourhood = get_neighbourhood)

        #super option
        residents = get_neighbourhood.member_set.all()

    context = {'residents': residents}
    return render(request, 'neighbourhoodx/residents.html', context)

def socialServices(request):
    user = request.user
    administrator = Administrator.objects.get(user = user)
    get_neighbourhood = Neighbourhood.objects.get(admin = administrator)

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        if request.method == 'POST':
            form = SocialServicesForm(request.POST)
            if form.is_valid():
                service = form.save(commit=False)
                service.neighbourhood = get_neighbourhood
                service.save()
            return redirect(adminDashboard)

        else:
            form = SocialServicesForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/social_services.html', context)

def post(request):
    user = request.user
    administrator = Administrator.objects.get(user = user)
    get_neighbourhood = Neighbourhood.objects.get(admin = administrator)

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.neighbourhood = get_neighbourhood
                post.poster = user
                post.save()
            return redirect(adminDashboard)

        else:
            form = PostForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/add_post.html', context)

@login_required(login_url='login')
def adjust(request):
    user = request.user
    administrator = Administrator.objects.get(user = user)

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        if request.method == 'POST':
            form = NeighbourhoodForm(request.POST, instance = get_neighbourhood)
            if form.is_valid():
                neighbourhood = form.save(commit=False, instance = get_neighbourhood)
                neighbourhood.admin = administrator
                neighbourhood.save()
            return redirect(adminDashboard)

        else:
            form = NeighbourhoodForm(instance = get_neighbourhood)

    context = {'form': form}
    return render(request, 'neighbourhoodx/set_up_neighbourhood.html', context)


@login_required(login_url='login')
def deleteNeighbourhood(request, pk):
    user = request.user
    administrator = Administrator.objects.get(user = user)

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)
    
    else:
        if request.user != get_neighbourhood.admin.user:
            return HttpResponse('This method is restricted')

        if request.method == 'POST':
            get_neighbourhood.delete()
            return redirect(registerPage)
    
    context = {'obj':get_neighbourhood}
    return render(request, 'neighbourhoodx/delete.html', context)

@login_required(login_url='login')
def deleteResident(request, pk):
    user = request.user
    get_resident = Member.objects.get(id = pk)
    administrator = Administrator.objects.get(user = user)

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)
    
    else:
        if request.user != get_neighbourhood.admin.user:
            return HttpResponse('This method is restricted')

        if request.method == 'POST':
            get_resident.delete()
            
            #increase the residents count
            members = Member.objects.filter(neighbourhood = get_neighbourhood)
            member_count = members.count()
            get_neighbourhood.occupants = member_count - 1
            get_neighbourhood.save() 
            return redirect(viewResidents)

         
    
    context = {'obj':get_resident}
    return render(request, 'neighbourhoodx/delete_resident.html', context)
