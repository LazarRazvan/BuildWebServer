FROM alpine:edge

RUN apk add --update py3-pip

RUN mkdir -p /usr/src/app
RUN mkdir -p /var/run/web/
COPY requirements.txt /usr/src/app

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt
RUN python3 -m pip install influxdb

COPY server.py /usr/src/app

COPY templates /usr/src/app/templates
COPY static /usr/src/app/static

EXPOSE 5000

CMD ["python3", "/usr/src/app/server.py"]
