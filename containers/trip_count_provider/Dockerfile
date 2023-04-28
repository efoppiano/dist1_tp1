FROM python
RUN pip3 install pika

COPY trip_count_provider/trip_count_provider.py /opt/app/trip_count_provider.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/trip_count_provider.py