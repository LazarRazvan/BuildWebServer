FROM alpine:edge

# Run python3 for out parser
RUN apk add --update py3-pip

# Create dirs and copy parser sources
RUN mkdir -p /usr/src/app
COPY requirements.txt /usr/src/app
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt
COPY parser.py /usr/src/app

# Create polling directory
RUN mkdir -p /var/run/results

# Run parser (specify influxdb container hostname)
CMD ["python3", "/usr/src/app/parser.py", "influxdb_server"]
