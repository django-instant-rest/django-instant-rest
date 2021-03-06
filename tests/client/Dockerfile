FROM python:3.6

COPY Pipfile .

COPY Pipfile.lock .

RUN pip install pipenv

RUN pipenv install

CMD pipenv run python src/resource_pattern.py