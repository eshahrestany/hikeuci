# syntax=docker/dockerfile:1

FROM python:3.12.7-bookworm

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["flask", "db", "upgrade"]
CMD ["gunicorn", "-w", "6", "--worker-class", "gevent", "app:create_app()"]