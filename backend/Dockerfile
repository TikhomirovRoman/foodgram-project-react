FROM python:3.9
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY /foodgram_backend/ .
# ENTRYPOINT ["tail", "-f", "/dev/null"]
CMD ["python", "./manage.py", "runserver", "0:8000"] 
