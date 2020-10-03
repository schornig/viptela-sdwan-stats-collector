FROM python:3

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /usr/src/app

COPY requirements.txt .

#RUN apk add --update --no-cache postgresql-client jpeg-dev
#RUN apk add --update --no-cache --virtual .tmp-build-deps \
#      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip3 install -r requirements.txt