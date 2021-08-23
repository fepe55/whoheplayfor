FROM python:3.9.6-alpine3.14

ADD requirements.txt /app/requirements.txt

ADD . /app
WORKDIR /app

RUN set -ex \
    && apk add --no-cache --virtual .build-deps build-base \
    && apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    # && apk add --no-cache --virtual .build-deps postgresql-dev \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir wheel \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && /env/bin/pip install --no-cache-dir gunicorn \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps \
    && /env/bin/python manage.py collectstatic \
    && /env/bin/python manage.py migrate


ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "whoheplayfor.wsgi"]
