FROM python
RUN pip3 install pika

COPY dist_mean_calculator/dist_mean_calculator.py /opt/app/dist_mean_calculator.py
COPY common /opt/app/common

ENTRYPOINT ["/bin/bash"]