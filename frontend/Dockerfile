FROM python:3.12.6-alpine3.20

WORKDIR /app

COPY . /app

RUN adduser --disabled-password user
RUN chown -R user:user /app

USER user

EXPOSE 3000