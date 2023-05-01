FROM python
RUN pip3 install pika
RUN pip3 install pyzmq

COPY client/client.py /opt/app/client.py
COPY common /opt/app/common

ENTRYPOINT ["/bin/bash"]