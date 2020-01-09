FROM alpine:edge

RUN apk add --update py3-pip

RUN mkdir -p /usr/src/app
RUN mkdir -p /var/run/parser
RUN mkdir -p /var/run/results

COPY requirements.txt /usr/src/app

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

COPY parser.py /usr/src/app

CMD ["python3", "/usr/src/app/parser.py"]
