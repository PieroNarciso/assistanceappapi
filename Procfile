release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn backend.wsgi:application --log-file - --log-level debug