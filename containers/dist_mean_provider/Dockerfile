FROM python
RUN pip3 install pika

COPY dist_mean_provider/dist_mean_provider.py /opt/app/dist_mean_provider.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/dist_mean_provider.py