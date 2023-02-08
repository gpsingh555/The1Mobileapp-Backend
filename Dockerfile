# syntax=docker/dockerfile:1

FROM python:3.8

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN apt-get update
# RUN apt-get install -y software-properties-common && apt-get update
# RUN  add-apt-repository ppa:ubuntugis/ppa &&  apt-get update
# RUN apt-get install -y gdal-bin libgdal-dev
# ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
# ARG C_INCLUDE_PATH=/usr/include/gdal

RUN apt-get update

ENV ENV=DEV
RUN apt-get install -y libgdal-dev
RUN apt-get install -y cron
RUN apt-get install -y vim nano
RUN touch /tmp/scheduled_job.log
RUN chmod 777 /tmp/scheduled_job.log


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt



# COPY ./config/celery/worker/start /start-celeryworker
# RUN sed -i 's/\r$//g' /start-celeryworker
# RUN chmod +x /start-celeryworker
#
# COPY ./config/celery/beat/start /start-celerybeat
# RUN sed -i 's/\r$//g' /start-celerybeat
# RUN chmod +x /start-celerybeat
#
# COPY ./config/celery/flower/start /start-flower
# RUN sed -i 's/\r$//g' /start-flower
# RUN chmod +x /start-flower

COPY . .
