FROM python
RUN pip3 install pika

COPY year_filter/year_filter.py /opt/app/year_filter.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/year_filter.py