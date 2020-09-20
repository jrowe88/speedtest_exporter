# Prometheus SpeedTest Exporter

Run internet speed test and export metrics to [Prometheus](http://prometheus.io).

## Getting started

### Run Script Directly
1. Download and install [SpeedTest CLI client](https://www.speedtest.net/apps/cli)

2. Install [Python 3](https://www.python.org/about/gettingstarted/)

3. Copy speedtest.py to your system

4. Run script in background

```bash
nohup python3 ./speedtest.py &>/dev/null &
```
5. Goto http://localhost:9497 to view metrics


### Run in Docker Container (Designed intention)

1. Pull Docker container:
```bash
docker pull jrowe88/speedtest_exporter
```
2. Run in a Docker container (as daemon). Optionally, specifiy ENV to configure ports, interval, and delay
```bash
docker run -d -p 9497:9497 --name speedtest_exporter jrowe88/speedtest_exporter
```

### Examples
1. Change default parameters
```bash

docker run -d -p 9191:9191 --env PORT=9191 --env INTERVAL_SECONDS=7200 --env STARTUPDELAY_SECONDS=5 --name speedtest_exporter jrowe88/speedtest_exporter

```

2. Setting up Prometheus Scraper Config
```bash

```

## Other resources

Grafana Dashboard: https://grafana.com/dashboards/12309

Prometheus configuration:



---

Copyright @ 2020 Jim Rowe