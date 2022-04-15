from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('admin-profile/', views.adminProfile, name="adminProfile"),
    path('set-up-neighbourhood/', views.setUpNeighbourhood, name="setUpNeighbourhood"),
    path('dashboard/', views.dashboard, name="dashboard"),
]

urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 