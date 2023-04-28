FROM python
RUN pip3 install pika

COPY dur_avg_provider/dur_avg_provider.py /opt/app/dur_avg_provider.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/dur_avg_provider.py