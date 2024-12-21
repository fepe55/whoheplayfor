FROM python:3.12-alpine

ADD requirements.txt /app/requirements.txt

ADD . /app
WORKDIR /app

RUN set -ex \
    && apk add --no-cache --virtual .build-deps build-base \
    && apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev libffi-dev postgresql-dev openssl-dev cargo \
    && apk add --no-cache bash \
    # && apk add --no-cache --virtual .build-deps postgresql-dev \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir wheel \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && /env/bin/pip install --no-cache-dir sentry-sdk \
    # && /env/bin/pip install --no-cache-dir psycopg2==2.8.6 \
    && /env/bin/pip install --no-cache-dir psycopg[binary] \
    && /env/bin/pip install --no-cache-dir gunicorn \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps \
    && /env/bin/python manage.py collectstatic --no-input

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "whoheplayfor.wsgi"]
