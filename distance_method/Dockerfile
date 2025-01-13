FROM python:3.10
COPY . /distance_method
WORKDIR /distance_method
RUN ["pip3", "install", "-r", "requirement2.txt"]
CMD ["python3", "manage.py", "runserver", "127.0.0.1:1985"]