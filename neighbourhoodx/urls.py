from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name="login"),

    ## admin
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('admin-profile/', views.adminProfile, name="adminProfile"),
    path('set-up-neighbourhood/', views.setUpNeighbourhood, name="setUpNeighbourhood"),
    path('admin-dashboard/', views.adminDashboard, name="adminDashboard"),
    path('add-resident/', views.addResident, name="add-resident"),
    path('view-residents/', views.viewResidents, name="view-residents"),
    path('social-services/', views.socialServices, name="social-services"),
    path('post/', views.post, name="post"),
    path('delete-any-post/<str:pk>/', views.deleteAnyPost, name="delete-any-post"),
    path('adjust/', views.adjust, name="adjust"),
    path('delete/<str:pk>/', views.deleteNeighbourhood, name="delete-neighbourhood"),
    path('delete-resident/<str:pk>/', views.deleteResident, name="delete-resident"),
    
    ## resident
    path('resident-dashboard/', views.residentDashboard, name="residentDashboard"),
    path('view-other-residents/', views.viewOtherResidents, name="view-other-residents"),
    path('resident-post/', views.residentPost, name="resident-post"),
    path('business/', views.business, name="business"),
    path('profile/<str:pk>/', views.profile, name="profile"),
    path('edit-profile/<str:pk>/', views.editProfile, name="edit-profile"),
    path('delete-post/<str:pk>/', views.deletePost, name="delete-post"),
    path('password-change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('password-reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),   
    # uidb64: The user’s id encoded in base 64.
    # token: Password recovery token to check that the password is valid.

]

urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 