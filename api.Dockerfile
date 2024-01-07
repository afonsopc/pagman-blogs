FROM python:3.11-alpine AS builder

WORKDIR /app

COPY ./api-blogs/requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY ./api-blogs /app

ENTRYPOINT ["python3"]
CMD ["app.py"]