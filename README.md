# Prometheus SpeedTest Exporter

Run internet speed test and export metrics to [Prometheus](http://prometheus.io).

## Getting started

### Run in Docker Container (Intended Use)

1. Pull Docker container:
```bash
docker pull jrowe88/speedtest_exporter
```
2. Run in a Docker container (detached). Optionally, specifiy environment parameters to configure ports, interval, and startup delay.
```bash
docker run -d -p 9497:9497 --name speedtest_exporter jrowe88/speedtest_exporter
```

### Run Script Directly
1. Download and install [SpeedTest CLI client](https://www.speedtest.net/apps/cli)

2. Install [Python 3](https://www.python.org/about/gettingstarted/)

3. Copy speedtest.py to your system

4. Run script in background

```bash
nohup python3 ./speedtest.py &>/dev/null &
```
5. Goto http://localhost:9497 to view metrics

### Examples
1. Change default parameters

>Note: SpeedTest downloads and uploads many MB of data over your connection.  Do not set the interval (INTERVAL_SECONDS) to be very short unless that is your intention and you understand the consequences to your internet traffic.  Default is 3600 seconds, or every 30 minutes.

```bash
docker run -d -p 9191:9191 --env PORT=9191 --env INTERVAL_SECONDS=7200 --env STARTUPDELAY_SECONDS=5 --name speedtest_exporter jrowe88/speedtest_exporter
```

2. Setting up Prometheus Scraper Config

>Add the following section to the prometheus.yml configuration file:

```bash
...
    - job_name: speed
    scrape_interval: 240s
    metrics_path: /
    static_configs:
    - targets:
        - 192.168.1.3:9497
...
```

>Reload the [Prometheus config](https://prometheus.io/docs/prometheus/latest/configuration/configuration/):

```bash
curl -X POST http://192.168.1.3:9091/-/reload
```

## Other resources

Grafana Dashboard: https://grafana.com/dashboards/12309

Prometheus configuration: https://prometheus.io/docs/prometheus/latest/configuration/configuration/



---

Copyright @ 2020 Jim Rowe