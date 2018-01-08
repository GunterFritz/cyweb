Web application to create the ikosaeder for Stafford Beers workshop method
Copyrigth Gunter Fritz

prerequisites
-python3
-django

#create a django-project
$django-admin startproject <projectname>

#setup a database, per default SQLlite, you can change it in <projectname>/settings.py
$python3 manage.py migrate

#create a superuser
$python3 manage.py createsuperuser
 username> admin
 email> admin@example.com
 password> admcyka99


#create the cyka app or copy the directory as app cyka or load from github
#new
$python3 manage.py startapp <appname>
#github


#add app to <projectname>/settings.py
INSTALLED_APPS = [
    'cyka.apps.CykaConfig',
...

#add url to <projectname>/urls.py
from django.conf.urls import include, url
urlpatterns = [
    url(r'^cyka/', include('cyka.urls')),
...

#create database models
$python manage.py makemigrations cyka 

#apply
$python3 manage.py migrate

#test
$python3 manage.py runserver

