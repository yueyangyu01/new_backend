# new_backend

Run these commands before running server

Pip install pipenv
Pipenv install djangorestframework
Pipenv install django-cors-headers

Create and activate virtual environment
virtualenv newenv
source newenv/bin/activate

Install Django:
pip install django

Database tables
Python manage.py make-migrations
Python manage.py migrate
Python manage.py createsuperuser

Run server:
Python manage.py runserver
