# Django Auth!

This tutorial will provide you with a basic authorizaiton suite that allows you to signup, login, and logout. You'll notice a protected route(s), a one-to-one relationship, and some extra goodies sprinkled in. Get your google hats strapped, this is going to be intense!

### Creating the Project structure.

1. Start a Django project called `authly`:

```bash
$ django-admin startproject authly .
$ django-admin startapp authly_app
$ mkdir authly_app/templates authly_app/media authly_app/static authly_app/media/profile_pics authly_app/templates/authly_app
```

Django also has models and views created for our app `authly_app` which should me migrated before we start making our own models. This will also set up our built-in `User` model. Make sure to setup Postgresql as our default database:

```bash
$ python3 manage.py migrate
```


### Modifying the Project Files.
Open up `authly/settings.py` and add the lines for other _DIR to look like :

```python
# authly/settings.py
# Build paths inside the project like this: os.path.join(BASE_DIR, …)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# add the below three lines
TEMPLATE_DIR = os.path.join(BASE_DIR,'authly_app/templates')
STATIC_DIR = os.path.join(BASE_DIR,'authly_app/static')
MEDIA_DIR = os.path.join(BASE_DIR,'authly_app/media')
```

Also In the Installed apps section you need to add `authly_app`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authly_app',
]
```

Add these lines at the end of our `authly/settings.py` for static, templates and media folder :

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR,]
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'
LOGIN_URL = '/authly_app/user_login/'
```

Next we create the `authly_app/models.py` to be used that will be the basis of our `forms.py`. Import Django's `User` model in `models.py`:

```python

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
  user = models.OneToOneField(User,on_delete=models.CASCADE)
  portfolio_site = models.URLField(blank=True)
  profile_pic = models.ImageField(upload_to='profile_pics',blank=True)

  def __str__(self):
    return self.user.username

```

Create a `forms.py` file in our `authly_app` folder

```python
# authly_app/forms.py
from django import forms
from authly_app.models import UserProfileInfo
from django.contrib.auth.models import User
  class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
      model = User
      fields = ('username','password','email')

  class UserProfileInfoForm(forms.ModelForm):
 
    class Meta():
      model = UserProfileInfo
      fields = ('portfolio_site','profile_pic')

```
Register your models in authly_app/admin.py too

```python
# authly_app/admin.py
from django.contrib import admin
from authly_app.models import UserProfileInfo
# Register your models here.
admin.site.register(UserProfileInfo)

```


In `authly_app/views.py`:

```python
# authly_app/views.py
from django.shortcuts import render, redirect
from authly_app.forms import UserForm, UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,'authly_app/index.html')

@login_required
def special(request):
    return HttpResponse("You are logged in !")

@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'authly_app/registration.html', {'user_form':user_form,'profile_form':profile_form,'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect('index')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print(f'They used username: {username} and password: {password}'
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'authly_app/login.html', {})
```

The templates can be arranged now for generating the views, we use four templates for this : `base.html`, `registration.html`, `login.html`, `index.html`

In `base.html`:
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Base</title>
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
</head>
  <body>
    <nav class="navbar navbar-default navbar-static-top">
      <div class="container">
        <ul class="nav navbar-nav">
          {# Django Home Link / Admin Link / Register Link#}
          <li><a class="navbar-brand" href="{% url 'index' %}">DJANGO</a></li>
          <li><a class="navbar-link" href="{% url 'admin:index' %}">Admin</a></li>
          <li><a class="navbar-link" href="{% url 'register' %}">Register</a></li>     
          {# Some logic on what to display for last item#}
          {% if user.is_authenticated %}
            <li><a href="{% url 'logout' %}">Logout</a></li>
          {% else %}
            <li><a class="navbar-link" href="{% url 'user_login' %}">Login</a></li>
          {% endif %}
        </ul>
      </div>
    </nav>
    <div class="container">
    {% block content %}
    {% endblock %}
    </div>
  </body>
</html>

```

In `index.html`:
```html
{% extends "authly_app/base.html" %}
{% block content %}
<div class="container">
  <div class="jumbotron">
    <h1>Welcome to the Djungle !</h1>
    {% if user.is_authenticated %}
        <h2>Hello {{ user.username }}</h2>
    {% else %}
        <h2>Register or Login if you'd like to</h2>
    {% endif %}
  </div>
</div>
{% endblock %}
```

In `login.html`:

```python
{% extends 'authly_app/base.html' %}
{% block content %}
  <div class="container">
    <div class="jumbotron">
      <h1>Login here :</h1>
        <form method="post" action="{% url 'user_login' %}">
          {% csrf_token %}
          {# A more "HTML" way of creating the login form#}
          <label for="username">Username:</label>
          <input type="text" name="username" placeholder="Username">
          <label for="password">Password:</label>
          <input type="password" name="password" placeholder="Password">
          <input type="submit" name="" value="Login">
        </form>
      </div>
    </div>
{% endblock %}
```

In `registration.html`:
```html
{% extends "authly_app/base.html" %}
{% load staticfiles %}
{% block content %}
  <div class="container">
    <div class="jumbotron">
      {% if registered %}

      <h1>Thank you for registering!</h1>
      
      {% else %}
      
      <h1>Register Here</h1>
        <h3>Just fill out the form.</h3>
        <form enctype="multipart/form-data" method="POST">
          {% csrf_token %}
          {{ user_form.as_p }}
          {{ profile_form.as_p }}
          <input type="submit" name="" value="Register">
        </form>
        
      {% endif %}
    </div>
  </div>
{% endblock %}
```

We then register the above urls into our **app** `urls.py` files for this create a file `authly_app/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns=[
  
    path('', views.index, name='index'),

    path('register', views.register, name='register'),
    path('user_login',views.user_login,name='user_login'),
    path('logout', views.user_logout, name='logout'),

    path('api/users', views.sendJson, name='sendJson'),
    path('special',views.special, name='special'),
]
```
In the main `urls.py` file the rest of the pattern is specified:

```python
# authly/urls.py
# authly/urls.py
from django.contrib import admin
from django.urls import path
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('authly_app.urls')),
]

```

Apply the migrations using

```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

Create a superuser using the command:

```bash
$ python3 manage.py createsuperuser
```

Enter your desired username, email and password.

Now you are ready to start your server!

```bash
$ python3 manage.py runserver
Performing system checks...
System check identified no issues (0 silenced).
September 11, 2018 - 04:03:03
Django version 2.0.5, using settings 'authly.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
