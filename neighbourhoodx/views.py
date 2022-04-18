from unicodedata import category
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
import random
import string
from urllib import request
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from geopy.distance import geodesic
from requests import get
from .emails import send_welcome_resident, send_welcome_email
from .forms import BusinessForm, CustomUserForm, AdministratorForm, MemberForm, NeighbourhoodForm, PostForm, SocialServicesForm, UpdateMemberForm, UpdateUserForm
from django.contrib.auth.decorators import login_required
from .models import Administrator, Neighbourhood, SocialServices, Member, Post, Business
import folium
from django.db.models import Q

# Create your views here.
## USER || ADMIN
@login_required(login_url='login')
def home(request):
    user = request.user
    
    try:
        administrator = Administrator.objects.get(user = user)
    except:
        administrator = None
    
    if administrator != None:
        return redirect(adminDashboard)

    else:
        try:
            member = Member.objects.get(user = user)
        except:
            pass
        if member != None:
            return redirect(residentDashboard)
        else:
            raise Http404()

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect(home)

    if request.method == 'POST':
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect(home)
        else:
            messages.error(request, 'Invalid username or Password')

    context = {'page': page}
    return render(request, 'neighbourhoodx/login_register.html', context) 

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect(loginPage)

## END USER || ADMIN

## ADMIN SECTION
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

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

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
    q = request.GET.get('q')
    if request.GET.get('q') != None:
        residents_search = Member.objects.filter(
            Q(user__username__icontains = q)&
            Q(neighbourhood = get_neighbourhood)
        )
        count_ = residents_search.count()
        m = None
        get_neighbourhood = None
        posts = None

    else:
        count_ = 0
        try:
            administrator = Administrator.objects.get(user = user)
        except:
            raise Http404()

        try:
            get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
            
        except:
            get_neighbourhood = None

        if get_neighbourhood != None:
            posts = get_neighbourhood.post_set.all()
            n_long = get_neighbourhood.location[0]
            n_lat = get_neighbourhood.location[1]   
            pointA = (n_lat, n_long)

            # residents
            residents = get_neighbourhood.member_set.all()
            # print(residents)
        
            #all services and businesses
            social_services = SocialServices.objects.filter(neighbourhood = get_neighbourhood)
            businesses = Business.objects.filter(neighbourhood = get_neighbourhood)
            # print(social_services)

            # specific services
            # ('bank','Bank'),
            # ('fire','Fire Department'),
            # ('police','Police Department'),
            # ('hospital', 'HealthCare'),  
            # ('school','School'), 

            banks = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'bank')
            fires = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'fire')
            polices = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'police')
            hospitals = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'hospital')
            print(hospitals)
            schools = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'school') 


            # folium map
            m = folium.Map([n_lat, n_long], zoom_start=12)

            #location marker
            folium.Marker([n_lat, n_long],
                popup=f'<strong>{get_neighbourhood.name}</strong> Neighbourhood',
                tooltip='Click here for more', 
                icon=folium.Icon(icon='home', color='blue')
                ).add_to(m)

            folium.CircleMarker(
                [n_lat, n_long],
                tooltip=f'<strong>{get_neighbourhood.name}</strong> Neighbourhood', 
                radius = 150,
                color='blue',
                weight=1,
            ).add_to(m)

            m.add_child(folium.LatLngPopup())

            # add residents to map
            if residents != None:
                for resident in residents:
                    r_long = resident.home_location[0]
                    r_lat = resident.home_location[1]
                    pointR = (r_lat, r_long)
                    distance = round(geodesic(pointA, pointR).km, 2)

                    line = folium.PolyLine([pointA, pointR], weight=3, color='blue', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([r_lat, r_long],
                        popup=f'<p><strong>resident-name: {resident.user.username}</strong></p> <p>contact: 0708957380</p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='blue', icon='user',)
                        ).add_to(m),

            # add businesses to map
            if businesses != None:
                for business in businesses:
                    s_long = business.location[0]
                    s_lat = business.location[1]

                    folium.Marker([s_lat, s_long],
                        popup=f'<p><strong>{business.name}</strong></p> <p>Owner: <strong>{business.owner}</strong> </p> <p>{business.description}</p> <p>reach out: {business.email}</p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='red', icon='shopping-cart',)
                        ).add_to(m),

            # all social services map
            # if social_services != None:
            #     for service in social_services:
            #         s_long = service.location[0]
            #         s_lat = service.location[1]

            #         folium.Marker([s_lat, s_long],
            #             popup=f'<strong>{service.name}</strong>',
            #             tooltip='Click here for more', 
            #             icon=folium.Icon(icon='cloud', color='red')
            #             ).add_to(m),

            # else:
            #     posts = None

            # specific social services' map
            # bank
            if banks != None:
                for bank in banks:
                    b_long = bank.location[0]
                    b_lat = bank.location[1]
                    pointB = (b_lat, b_long) 
                    distance = round(geodesic(pointA, pointB).km, 2)
                    print(distance)

                    line = folium.PolyLine([pointA, pointB], weight=3, color='orange', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([b_lat, b_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {bank.name}</strong></p> <span>Category: {bank.category}</span> <p>Hotline: <strong>{bank.hotline}</strong></p> ',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='orange', icon='credit-card')
                        ).add_to(m),

            # hospital
            if fires != None:
                for fire in fires:
                    f_long = fire.location[0]
                    f_lat = fire.location[1]

                    pointF = (f_lat, f_long) 
                    distance = round(geodesic(pointA, pointF).km, 2)

                    line = folium.PolyLine([pointA, pointF], weight=3, color='red', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([f_lat, f_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {fire.name}</strong></p> <span>Category: {fire.category}</span> <p>Hotline: <strong>{fire.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='red', icon='fire')
                        ).add_to(m),

            # police
            if polices != None:
                for police in polices:
                    p_long = police.location[0]
                    p_lat = police.location[1]

                    pointP = (p_lat, p_long) 
                    distance = round(geodesic(pointA, pointP).km, 2)

                    line = folium.PolyLine([pointA, pointP], weight=3, color='black',tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([p_lat, p_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {police.name}</strong></p> <span>Category: {police.category}</span> <p>Hotline: <strong>{police.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='black', icon='flag')
                        ).add_to(m),

            # hospital
            if hospitals != None:
                for hospital in hospitals:
                    h_long = hospital.location[0]
                    h_lat = hospital.location[1]

                    pointH = (h_lat, h_long)
                    distance = round(geodesic(pointA, pointH).km, 2)

                    line = folium.PolyLine([pointA, pointH], weight=3, color='purple',tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([h_lat, h_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {hospital.name}</strong></p> <span>Category: {hospital.category}</span> <p>Hotline: <strong>{hospital.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='purple', icon='heart')
                        ).add_to(m),

            # schools
            if schools != None:
                for school in schools:
                    s_long = school.location[0]
                    s_lat = school.location[1]

                    pointS = (s_lat, s_long) 
                    distance = round(geodesic(pointA, pointS).km, 2)

                    line = folium.PolyLine([pointA, pointS], weight=3, color='green', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([s_lat, s_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {school.name}</strong></p> <span>Category: {school.category}</span> <p>Hotline: <strong>{school.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='green', icon='book')
                        ).add_to(m),
                            
        else:
            posts = None
            return redirect(setUpNeighbourhood)


        m = m._repr_html_() #html representation
        residents_search = None
        count_ = None
    
    context = {'count_' :count_,'map': m, 'hood': get_neighbourhood, 'posts':posts, 'residents_search': residents_search}
    return render(request, 'neighbourhoodx/admin_dashboard.html', context)

@login_required(login_url='login')
def addResident(request):
    user = request.user

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

    try:
        get_neighbourhood = Neighbourhood.objects.get(admin = administrator)
    except:
        get_neighbourhood = None

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        if request.method == 'POST':
            form = MemberForm(request.POST)
            # print(form)
            if form.is_valid():
                new_res = form.save(commit=False)
                new_res.name = form.cleaned_data['name']
                new_res.username = form.cleaned_data['username']
                new_res.email = form.cleaned_data['email']
                new_list = request.POST.get('home_location')

                # reverse latitude and longitude
                # print(new_list)
                new = new_list.split(",")
                loc = reversed(new)
                str = ""
                for i in loc:
                    str += i + ","
                    print(i)
                # print(str)
                reverse_lat_len = list(str)
                # print(reverse_lat_len)
                reverse_lat_len.pop()
                # print(f)
                reverse_lat_len = ''.join(reverse_lat_len)
                print(reverse_lat_len)

                new_res.home_location = reverse_lat_len
                new_res.neighbourhood = get_neighbourhood

                #generates random password for the resident
                password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

                # creates user with the given details and returns it
                resident_user = User.objects.create_user(username = new_res.username, email = new_res.email, password = password)
                new_res.user = resident_user
                new_res.save()               
                
                #increase the residents count
                members = Member.objects.filter(neighbourhood = get_neighbourhood)
                member_count = members.count()
                get_neighbourhood.occupants = member_count + 1
                get_neighbourhood.save()
                
                #send email to resident
                send_welcome_resident(new_res.name,new_res.username,password,administrator.user.username ,get_neighbourhood.name, new_res.email)
            
            return redirect(adminDashboard)

        else:
            form = MemberForm()
      
    context = {'form': form, 'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/add_resident.html', context)

def viewResidents(request):
    user = request.user

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

    get_neighbourhood = Neighbourhood.objects.get(admin = administrator)

    if get_neighbourhood is None:
        return redirect(setUpNeighbourhood)

    else:
        #basic option
        # residents = Member.objects.filter(neighbourhood = get_neighbourhood)

        #super option
        residents = get_neighbourhood.member_set.all()

    context = {'residents': residents,  'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/residents.html', context)

def socialServices(request):
    user = request.user

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

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

    context = {'form': form, 'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/social_services.html', context)

def post(request):
    user = request.user

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

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

    context = {'form': form, 'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/add_post.html', context)

@login_required(login_url='login')
def adjust(request):
    user = request.user

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

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
                neighbourhood = form.save(commit=False)
                neighbourhood.admin = administrator
                neighbourhood.save()
            return redirect(adminDashboard)

        else:
            form = NeighbourhoodForm(instance = get_neighbourhood)

    context = {'form': form, 'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/set_up_neighbourhood.html', context)


@login_required(login_url='login')
def deleteNeighbourhood(request, pk):
    user = request.user

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

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
    
    context = {'obj':get_neighbourhood, 'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/delete.html', context)

@login_required(login_url='login')
def deleteResident(request, pk):
    user = request.user
    get_resident = Member.objects.get(id = pk)

    try:
        administrator = Administrator.objects.get(user = user)
    except:
        raise Http404()

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

#END OF ADMIN SECTION

## RESIDENT SECTION
@login_required(login_url='login')
def residentDashboard(request):
    user = request.user
    resident = Member.objects.get(user = user)
    get_neighbourhood = resident.neighbourhood

    q = request.GET.get('q')
    if request.GET.get('q') != None:
        residents_search = Member.objects.filter(
            Q(user__username__icontains = q) &
            Q(neighbourhood = get_neighbourhood) 
        )
        count_ = residents_search.count()
        m = None
        get_neighbourhood = None
        posts = None

    else:
        if get_neighbourhood != None:
            posts = get_neighbourhood.post_set.all()
            n_long = get_neighbourhood.location[0]
            n_lat = get_neighbourhood.location[1] 
            
            
            #all services and businesses
            social_services = SocialServices.objects.filter(neighbourhood = get_neighbourhood)
            businesses = Business.objects.filter(neighbourhood = get_neighbourhood)
            print(social_services)

            # specific services
            # ('bank','Bank'),
            # ('fire','Fire Department'),
            # ('police','Police Department'),
            # ('hospital', 'HealthCare'),  
            # ('school','School'), 

            banks = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'bank')
            fires = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'fire')
            polices = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'police')
            hospitals = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'hospital')
            print(hospitals)
            schools = SocialServices.objects.filter(neighbourhood = get_neighbourhood, category = 'school') 

          

            # add user to map
            try:
                get_home = resident.home_location
               
            except:
                pass

            if get_home != None:
                gh_long = get_home[0]
                gh_lat = get_home[1] 

                # folium map
                m = folium.Map(location=[gh_lat, gh_long], zoom_start=11)
                pointA =(gh_lat, gh_long)

                folium.Marker([gh_lat, gh_long],
                    popup=f'<p><strong>resident-name: {resident.user.username}</strong></p> <p>contact: 0708957380</p>',
                    tooltip='Click here for more', 
                    icon=folium.Icon(color='red', icon='pushpin',)
                    ).add_to(m),

            # add other residents to map
            residents = get_neighbourhood.member_set.all()

            # add residents to map
            if residents != None:
                for resident in residents:
                    if resident.user == request.user:
                        pass
                    else:
                        r_long = resident.home_location[0]
                        r_lat = resident.home_location[1]
                        pointR = (r_lat, r_long)
                        distance = round(geodesic(pointA, pointR).km, 2)

                        line = folium.PolyLine([pointA, pointR], weight=3, color='blue', tooltip=f'{distance} km')
                        m.add_child(line)

                        folium.Marker([r_lat, r_long],
                            popup=f'<p><strong>resident-name: {resident.user.username}</strong></p> <p>contact: 0708957380</p>',
                            tooltip='Click here for more', 
                            icon=folium.Icon(color='blue', icon='user',)
                            ).add_to(m),

            #location marker
            folium.Marker([n_lat, n_long],
                popup=f'<strong>{user.username}</strong> Neighbourhood <p>where you belong</p>',
                tooltip='Click here for more', 
                icon=folium.Icon(icon='home', color='blue')
                ).add_to(m)

            

            folium.CircleMarker(
                [n_lat, n_long],
                tooltip=f'<strong>{get_neighbourhood.name}</strong> Neighbourhood', 
                radius = 150,
                color='blue',
                weight=1,
            ).add_to(m)

            m.add_child(folium.LatLngPopup())

            # add businesses to map
            if businesses != None:
                for business in businesses:
                    s_long = business.location[0]
                    s_lat = business.location[1]

                    folium.Marker([s_lat, s_long],
                        popup=f'<p><strong>{business.name}</strong></p> <p>Owner: <strong>{business.owner}</strong> </p> <p>{business.description}</p> <p>reach out: {business.email}</p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='red', icon='shopping-cart',)
                        ).add_to(m),

            # all social services map
            # if social_services != None:
            #     for service in social_services:
            #         s_long = service.location[0]
            #         s_lat = service.location[1]

            #         folium.Marker([s_lat, s_long],
            #             popup=f'<strong>{service.name}</strong>',
            #             tooltip='Click here for more', 
            #             icon=folium.Icon(icon='cloud', color='red')
            #             ).add_to(m),

            # else:
            #     posts = None

            # specific social services' map
            # bank
            if banks != None:
                for bank in banks:
                    b_long = bank.location[0]
                    b_lat = bank.location[1]
                    pointB = (b_lat, b_long) 
                    distance = round(geodesic(pointA, pointB).km, 2)
                    print(distance)

                    line = folium.PolyLine([pointA, pointB], weight=3, color='orange', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([b_lat, b_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {bank.name}</strong></p> <span>Category: {bank.category}</span> <p>Hotline: <strong>{bank.hotline}</strong></p> ',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='orange', icon='credit-card')
                        ).add_to(m),

            # hospital
            if fires != None:
                for fire in fires:
                    f_long = fire.location[0]
                    f_lat = fire.location[1]

                    pointF = (f_lat, f_long) 
                    distance = round(geodesic(pointA, pointF).km, 2)

                    line = folium.PolyLine([pointA, pointF], weight=3, color='red', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([f_lat, f_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {fire.name}</strong></p> <span>Category: {fire.category}</span> <p>Hotline: <strong>{fire.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='red', icon='fire')
                        ).add_to(m),

            # police
            if polices != None:
                for police in polices:
                    p_long = police.location[0]
                    p_lat = police.location[1]

                    pointP = (p_lat, p_long) 
                    distance = round(geodesic(pointA, pointP).km, 2)

                    line = folium.PolyLine([pointA, pointP], weight=3, color='black',tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([p_lat, p_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {police.name}</strong></p> <span>Category: {police.category}</span> <p>Hotline: <strong>{police.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='black', icon='flag')
                        ).add_to(m),

            # hospital
            if hospitals != None:
                for hospital in hospitals:
                    h_long = hospital.location[0]
                    h_lat = hospital.location[1]

                    pointH = (h_lat, h_long)
                    distance = round(geodesic(pointA, pointH).km, 2)

                    line = folium.PolyLine([pointA, pointH], weight=3, color='purple',tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([h_lat, h_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {hospital.name}</strong></p> <span>Category: {hospital.category}</span> <p>Hotline: <strong>{hospital.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='purple', icon='heart')
                        ).add_to(m),

            # schools
            if schools != None:
                for school in schools:
                    s_long = school.location[0]
                    s_lat = school.location[1]

                    pointS = (s_lat, s_long) 
                    distance = round(geodesic(pointA, pointS).km, 2)

                    line = folium.PolyLine([pointA, pointS], weight=3, color='green', tooltip=f'{distance} km')
                    m.add_child(line)

                    folium.Marker([s_lat, s_long],
                        popup=f'<p style="width:10rem;"><strong>Name: {school.name}</strong></p> <span>Category: {school.category}</span> <p>Hotline: <strong>{school.hotline}</strong></p>',
                        tooltip='Click here for more', 
                        icon=folium.Icon(color='green', icon='book')
                        ).add_to(m),
                            
    
        else:
            posts = None
            return redirect(loginPage)

        m = m._repr_html_() #html representation
        residents_search = None
        count_ = None
        
    context = {'count_' :count_,'map': m, 'hood': get_neighbourhood, 'posts':posts, 'residents_search': residents_search}
    return render(request, 'neighbourhoodx/resident_dashboard.html', context)

@login_required(login_url='login')
def viewOtherResidents(request):
    user = request.user

    try:
        resident = Member.objects.get(user = user)
    except:
        raise Http404()

    get_neighbourhood = resident.neighbourhood

    if get_neighbourhood is None:
        raise Http404()

    else:
        #basic option
        # residents = Member.objects.filter(neighbourhood = get_neighbourhood)

        #super option
        residents = get_neighbourhood.member_set.all()

    context = {'residents': residents, 'hood':get_neighbourhood,}
    return render(request, 'neighbourhoodx/residents_res.html', context)

@login_required(login_url='login')
def residentPost(request):
    user = request.user

    try:
        resident = Member.objects.get(user = user)
    except:
        raise Http404()

    get_neighbourhood = resident.neighbourhood

    if get_neighbourhood is None:
        raise Http404()

    else:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.neighbourhood = get_neighbourhood
                post.poster = user
                post.save()
            return redirect(residentDashboard)

        else:
            form = PostForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/add_post_res.html', context)

@login_required(login_url='login')
def business(request):
    user = request.user

    try:
        resident = Member.objects.get(user = user)
        print(resident)
        print(resident.home_location)

    except:
        raise Http404()

    get_neighbourhood = resident.neighbourhood
    print(get_neighbourhood)

    if get_neighbourhood is None:
        raise Http404()

    else:
        n_long = get_neighbourhood.location[0]
        n_lat = get_neighbourhood.location[1]
        print(n_long)
        print(resident.home_location[0])

        # # try to overide and set new location coordinates -- first try:)
        # l_list = list(resident.home_location)
        # print(l_list[0])
        # l_list[0] = n_long
        # l_list[1] = n_lat
        # print(l_list[0])

        # l_tuple = tuple(l_list)
        # print(l_tuple)

        # resident.home_location = l_tuple
        # print(resident.home_location)
        # resident.save()

        # resident.home_location[0] = n_long
        # resident.home_location[1] = n_lat
        # resident.save()

        Business.setCenterLocation(n_long, n_lat)

        if request.method == 'POST':
            form = BusinessForm(request.POST)
            if form.is_valid():
                business = form.save(commit=False)
                business.owner = user
                business.neighbourhood = get_neighbourhood
                business.save()
            return redirect(residentDashboard)

        else:
            form = BusinessForm()

    context = {'form': form}
    return render(request, 'neighbourhoodx/add_business.html', context)

@login_required(login_url='login')
def profile(request, pk):
    user = request.user
    resident = Member.objects.get(user = user)

    profile = User.objects.get(id = user.id)

    context = {'profile': profile, 'resident':resident,}
    return render(request, 'neighbourhoodx/profile.html', context)

@login_required(login_url='login')
def editProfile(request, pk):
    user = request.user
    resident = Member.objects.get(user = user)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateMemberForm(request.POST, request.FILES, instance=resident)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            prof = profile_form.save(commit=False)
            prof.save()
            return redirect('profile',  request.user.id)
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateMemberForm(instance=resident)

    context = {'user_form': user_form, 'profile_form': profile_form, 'resident': resident,}

    return render(request, 'neighbourhoodx/edit_profile.html', context)

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'neighbourhoodx/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy(residentDashboard)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'neighbourhoodx/password_reset.html'
    email_template_name = 'neighbourhoodx/password_reset_email.html'
    subject_template_name = 'neighbourhoodx/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')