# A Tourism Platform
 _made with_ ⬇ <br/>  [<img src="https://static.djangoproject.com/img/logos/django-logo-negative.png" alt="Django" width="75">](https://www.djangoproject.com/) 
<br/>
<br/>
✨ A tourism managment System server Backend made with Django and Celery <br/>
a system relying on digital ticket based reservations for activities posted by administrators ✨

## Features
- Automatic Translations and full localizations including static message translations and localized currencies currently supporting 5 languages
- Ai django App that relies on Google Gemini to query questions and pass data to the model also localized and logs responses to the database
- Currencies and Exchange rates
- JWT authentication and OAuth2 authentication currently setup with Google OAuth2
- Real Time push notifications and inbox notifications using Google Firebase
- Delayed tasks on the worker for performence heavy tasks such as many slow api calls and scheduled tasks for events

### To run the server from django built in dev server
- setup the .env file in src example given in .env.example
- open your shell in the global dir of the repo and run:<br/>
make sure you have python first:
```sh
python --version
```
```sh
pip install pipenv
pipenv install
pipenv shell
cd src
py manage.py migrate
py manage.py compilemessages
py manage.py runserver
```

The Django Base dir is in src
<br/>

### Run a Celery Worker for executing tasks and Celery Beat for scheduling

```sh
celery -A tourism.celery beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
```sh
celery -A tourism.celery worker -P gevent -l INFO
```

