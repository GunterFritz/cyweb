Web application to create the ikosaeder for Stafford Beers workshop method
Copyrigth Gunter Fritz

prerequisites
-python3
-django

#setup a database, per default SQLlite, you can change it in cyweb/settings.py
$python3 manage.py migrate

#create a superuser
$python3 manage.py createsuperuser
 username> admin
 email> admin@example.com
 password> admcyka99


#create database models
$python manage.py makemigrations cyka 

#apply database models
$python3 manage.py migrate

#start server
$python3 manage.py runserver

#login first
http://localhost:8000/admin/

#connect to startpage
http://localhost:8000/cyka/project/list/
