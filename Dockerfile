FROM python:3.6

RUN pip install pipenv

RUN git clone https://github.com/django-instant-rest/starter-template.git

WORKDIR /starter-template

RUN pipenv install

RUN pipenv run python manage.py migrate

CMD pipenv run python manage.py runserver 0.0.0.0:4000
