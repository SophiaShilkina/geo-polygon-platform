FROM python:3.12.6-alpine3.20

WORKDIR /app

COPY requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt

COPY . /app

RUN adduser --disabled-password user
RUN chown -R user:user /app

USER user

EXPOSE 8001