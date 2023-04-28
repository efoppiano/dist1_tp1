FROM python
RUN pip3 install pika

COPY simple_station_aggregator/simple_station_aggregator.py /opt/app/simple_station_aggregator.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/simple_station_aggregator.py