FROM ubuntu:jammy

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3 python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

COPY . /app

RUN touch requirements.txt
RUN pip install uwsgi
RUN pip install -r requirements.txt

CMD ["/usr/local/bin/uwsgi", "--ini", "/app/uwsgi.ini", "--http", "0.0.0.0:3000"]
