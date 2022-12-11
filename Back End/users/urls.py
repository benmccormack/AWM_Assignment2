from .views import RegisterAPI, LoginAPI, update_database, QueryOverpass
from django.urls import path
from knox import views as knox_views
from . import views

urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('api/updatedb/', views.update_database, name='updatedb'),
    path('api/getpubs/', QueryOverpass.as_view(), name="getpubs"),
    path('api/checkauthentication/', views.check_authentication, name="checkauthentication")
]