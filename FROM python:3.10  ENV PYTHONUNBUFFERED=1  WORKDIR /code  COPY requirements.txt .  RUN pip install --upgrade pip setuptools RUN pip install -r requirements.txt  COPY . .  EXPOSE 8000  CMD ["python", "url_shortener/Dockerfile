FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "url_shortener/manage.py", "runserver", "0.0.0.0:8000"]
