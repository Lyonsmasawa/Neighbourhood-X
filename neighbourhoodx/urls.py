from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('admin-profile/', views.adminProfile, name="adminProfile"),
    path('set-up-neighbourhood/', views.setUpNeighbourhood, name="setUpNeighbourhood"),
    path('admin-dashboard/', views.adminDashboard, name="adminDashboard"),
    path('add-resident/', views.addResident, name="add-resident"),
    path('view-residents/', views.viewResidents, name="view-residents"),
    path('social-services/', views.socialServices, name="social-services"),
    path('post/', views.post, name="post"),
    path('adjust/', views.adjust, name="adjust"),
    path('delete/<str:pk>/', views.deleteNeighbourhood, name="delete-neighbourhood"),
    path('delete/<str:pk>/', views.deleteResident, name="delete-resident"),
]

urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 