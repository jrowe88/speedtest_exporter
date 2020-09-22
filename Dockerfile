FROM debian:buster-slim AS get-speedtest

RUN apt-get update && apt-get install gnupg1 apt-transport-https dirmngr lsb-release -y
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61
RUN echo "deb https://ookla.bintray.com/debian $(lsb_release -sc) main" | tee  /etc/apt/sources.list.d/speedtest.list
RUN apt-get update
RUN apt-get install -y speedtest


FROM python:3-slim-buster as prod
RUN apt-get update

ENV PYTHONUNBUFFERED=0

#speedtest
COPY --from=get-speedtest /usr/bin/speedtest /usr/bin/speedtest

#exporter
RUN pip3 install prometheus_client
RUN apt install -y build-essential
RUN pip3 install Twisted
COPY *.py /usr/src/app/

#scripts and environment
ENV INTERVAL_SECONDS=1800 \
    STARTUPDELAY_SECONDS=15 \
    PORT=9497

ENTRYPOINT ["python3", "-u", "/usr/src/app/speedtest.py"]

