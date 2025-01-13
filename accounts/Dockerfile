FROM python:3.10
COPY . /accounts
WORKDIR /accounts
RUN ["pip3", "install", "-r", "requirement1.txt"]
CMD ["python3", "manage.py", "runserver", "127.0.0.1:1984"]