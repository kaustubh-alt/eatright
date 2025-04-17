from django.contrib import admin
from django.urls import path , include
from . import views
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings

class CSRFTokenView(APIView):
    def get(self, request):
        csrf_token = get_token(request)
        print(csrf_token)
        return Response({'csrfToken': csrf_token})

def logoutuser(request):
    logout(request)
    return redirect("/")


urlpatterns = [
    path('',views.output,name='output' ),
    path('activity/<str:fav>',views.likes,name='output' ),
    path('likedish',views.likedish,name='like_dish' ),  
    path("api/csrf/",CSRFTokenView.as_view(),name="csrf_token"),
    path('login',views.dashboard,name='login'),
    path('logout-user',logoutuser,name="logout"), 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

