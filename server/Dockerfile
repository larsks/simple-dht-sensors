FROM python:3.9

RUN mkdir /src
WORKDIR /src

RUN pip install pipenv
COPY Pipfile /src
RUN pipenv install
COPY dhtmetrics.py /src

CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:8000", "dhtmetrics:app"]
