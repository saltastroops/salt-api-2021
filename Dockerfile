# Dockerfile for creating the SALT API server

# WARNING: This Dockerfile is not suitable for production use.

# Based on https://fastapi.tiangolo.com/deployment/docker/

FROM python:3.9 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM ubuntu:20.04

# LABEL specifies the File Author / Organization
LABEL author="SALT Software Team <saltsoftware@saao.ac.za>"

EXPOSE 80

WORKDIR /app

RUN apt-get update -y
RUN export LANG=C.UTF-8
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y python3.9 python3.9-dev python3.9-distutils python3-pip
RUN apt-get install -y default-jre
RUN apt-get install -y imagemagick

# Give ImageMagick access to pdf files
RUN sed -i "s@<policy domain=\"coder\" rights=\"none\" pattern=\"PDF\" />@<policy domain=\"coder\" rights=\"read|write\" pattern=\"PDF\" />@g" /etc/ImageMagick-6/policy.xml

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip install wheel
RUN pip install salt_finder_charts

COPY ./saltapi /app/saltapi

RUN mkdir /var/www
RUN mkdir /var/www/.astropy
RUN chown www-data:www-data /var/www/.astropy

USER www-data:www-data

RUN mkdir /tmp/.PIPT

CMD ["uvicorn", "saltapi.main:app", "--host", "0.0.0.0", "--port", "80"]
