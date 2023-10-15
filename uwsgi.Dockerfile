FROM alpine:latest

RUN apk update
RUN apk add --no-cache python3 py3-pip python3-dev build-base libressl-dev libffi-dev

COPY . /app

RUN touch /app/requirements.txt

RUN pip3 install uwsgi
RUN pip3 install -r /app/requirements.txt

CMD ["uwsgi", "--ini", "/app/uwsgi.ini", "--http", "0.0.0.0:3000"]