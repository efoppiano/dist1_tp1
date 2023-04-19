FROM python
RUN pip3 install pika

COPY prec_filter/prec_filter.py /opt/app/prec_filter.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/prec_filter.py