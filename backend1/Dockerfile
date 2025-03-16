FROM python:3.12.6-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*\
    postgresql-client

COPY requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt

COPY . /app

RUN useradd -m user
RUN chown -R user:user /app

USER user

EXPOSE 8000