## Tourism Managment System BACKEND
A tourism managment System server Backend made with Django 5

## To run the server from django built in dev server
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

to run celery for scheduled task open the command line and run the following each line in a seperate command line window

```sh
celery -A tourism.celery beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
```sh
celery -A tourism.celery worker -P gevent -l INFO
```

