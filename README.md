Requirements
------------

- Python 3.4.3
- Django 1.11.3
- Postgres

Installation
------------
Following are the steps to install this platform.

- Get in the root directory of the project
- Create Virtual Environment
```sh
$ cd ..
$ virtualenv -p python3 backend
$ source backend/bin/activate
```
- Install Requirements
```sh
$ pip install -r requirements.txt
```
- Setting up the Database
```sh
$ cd django_rest_jwt
$ pwd //It should display like this "/Users/(user)/django_rest_jwt/django_rest_jwt"
$ sudo vim local_settings.py
    //Add the code below and save the file
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'django_rest_jwt',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
    // Note: Settings are for POSTGRES SQL
$ cd .. 
$ python manage.py migrate 
```
