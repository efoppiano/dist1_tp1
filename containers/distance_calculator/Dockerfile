FROM python
RUN pip3 install pika
RUN pip3 install haversine

COPY distance_calculator/distance_calculator.py /opt/app/distance_calculator.py
COPY common /opt/app/common

ENTRYPOINT python3 /opt/app/distance_calculator.py