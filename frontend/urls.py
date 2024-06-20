from django.urls import path, include
from django.conf import settings
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('add_url', add_url, name='add_url'),
    path('recordings', recordings, name='recordings'),
    path('events', events, name='events'),
    path('view_video/<str:video>/', view_video, name='view_video'),
    path('view_video/<str:video>', view_video, name='view_video'),
    path('setting', setting, name='setting'),
]
