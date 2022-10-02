FROM ghcr.io/illallangi/telegraf:v0.0.9
ENV INFLUXDB_DATABASE=uptimerobot \
    TELEGRAF_INTERVAL=1200

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY telegraf.conf /etc/telegraf/telegraf.conf

COPY ./telegraf_stockdata.py /usr/src/app/telegraf_stockdata.py
