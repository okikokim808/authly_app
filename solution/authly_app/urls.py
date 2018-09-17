from django.urls import path
from . import views

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
  
    path('', views.index, name='index'),

    path('register', views.register, name='register'),
    path('user_login',views.user_login,name='user_login'),
    path('logout', views.user_logout, name='logout'),

    path('api/users', views.sendJson, name='sendJson'),
    path('special',views.special, name='special'),
]