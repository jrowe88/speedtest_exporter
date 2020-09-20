FROM debian:buster-slim AS get-speedtest

RUN apt-get update && apt-get install gnupg1 apt-transport-https dirmngr lsb-release -y
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61
RUN echo "deb https://ookla.bintray.com/debian $(lsb_release -sc) main" | tee  /etc/apt/sources.list.d/speedtest.list
RUN apt-get update
RUN apt-get install speedtest


FROM python:3-slim-buster as prod

#speedtest
COPY --from=get-speedtest /usr/bin/speedtest /usr/bin/speedtest

#exporter
COPY *.py /usr/src/app/
RUN pip install prometheus_client

#scripts and environment
ENV INTERVAL_SECONDS=3600 \
    STARTUPDELAY_SECONDS=60 \
    PORT=9497

ENTRYPOINT ["python3", "/usr/src/app/speedtest.py"]
