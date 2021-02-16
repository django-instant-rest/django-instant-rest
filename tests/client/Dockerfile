FROM python:3.6

COPY . .

RUN pip install pipenv

RUN pipenv install

CMD pipenv run python resource_pattern.py