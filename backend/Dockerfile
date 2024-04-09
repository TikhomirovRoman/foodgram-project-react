FROM python:3.9

WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY ./foodgram_backend .
RUN python ./manage.py collectstatic
RUN mkdir static
RUN mkdir static/backend_static
RUN cp -r ./collected_static/. ./static/backend_static
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]