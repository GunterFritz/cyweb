FROM python:3.6

ENV PYTHONUNBUFFERED=1
WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

RUN python manage.py makemigrations
RUN python manage.py makemigrations cyka
RUN python manage.py migrate

CMD ["gunicorn", "--bind", "0.0.0.0:8000",  "cyweb.wsgi"]


EXPOSE 8000
