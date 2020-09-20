#perform a internet speed test using SpeedTest cli
#report results using the prometheus client
#some parameters set from the system environment:
#  PORT - port for reporing metrics
#  sss - delay in seconds for running speedtest after startup (default =  15 seconds)
#  xxx - interval in sectinos between speedtest (default = 3600 seconds)
#  ggg - specified gateway ip (optional)

from prometheus_client import (Gauge, start_http_server)
import time, os, subprocess, json
from datetime import datetime

def printLog(entry: str):    
    print(f"{datetime.now()} - {entry}")

printLog("Speedtest exporter started.")

#setup run parameters
config = {'port': 9497,
        'interval': 3600,
        'delay': 60}

if os.getenv("PORT") != None:
    config["port"] = int(os.getenv("PORT"))

if os.getenv("INTERVAL_SECONDS") != None:
    config["interval"] = int(os.getenv("INTERVAL_SECONDS"))

if os.getenv("STARTUPDELAY_SECONDS") != None:
    config["delay"] = int(os.getenv("STARTUPDELAY_SECONDS"))

printLog(f'exporter port={config["port"]}')
printLog(f'startup delay={config["port"]} s')
printLog(f'interval={config["port"]} s')

#create metrics
ts = Gauge('speedtest_timestamp', 'Timestamp of the speedtest in Unix time.')
jitter = Gauge('speedtest_ping_jitter_seconds','Ping jitter in seconds.')
latency = Gauge('speedtest_ping_latency_seconds', 'Ping latency in seconds.')
packetloss = Gauge('speedtest_packet_loss', 'Packet loss during speed test.')
interface = Gauge('speedtest_interface_info','Information about the interface used for the test, value is always 1.',
    ['internalIp','name','macAddr','isVpn','externalIp'])
server = Gauge('speedtest_server_info','Information about the interface used for the speedtest, value is always 1.',
    ['id','name','location','country','host','port','ip'])
isp = Gauge('speedtest_isp_info', 'Detected Internet Service Provider info, value is always 1.', ['isp'])
downloadBandwidth = Gauge('speedtest_download_bytes_per_second', 'Download speed in bytes/second.')
downloadBytes = Gauge('speedtest_download_bytes', 'Downloaded bytes.')
downloadElapsed = Gauge('speedtest_download_seconds', 'Time to complete download in seconds.')
uploadBandwidth = Gauge('speedtest_upload_bytes_per_second', 'Upload speed in bytes/second.')
uploadBytes = Gauge('speedtest_upload_bytes', 'Uploaded bytes.')
uploadElapsed = Gauge('speedtest_upload_seconds', 'Time to complete upload in seconds.')

#Run the SpeedTest cli and return parsed json
def runSpeedTest() -> json:
    printLog("Running speedtest")
    complete = subprocess.run(["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"], 
                            stdout=subprocess.PIPE, shell=False) 
    return json.loads(complete.stdout)

#Update the metric values
def updateValues(results: json):
    printLog("Updating values")
    tsValue = datetime.strptime(results["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
    ts.set(tsValue.timestamp())
    jitter.set(results["ping"]["jitter"]/1000)
    latency.set(results["ping"]["latency"]/1000)
    packetloss.set(results["packetLoss"])
    isp.labels(isp=results["isp"]).set(1)
    interface.labels(internalIp=results["interface"]["internalIp"],
        name=results["interface"]["name"],         
        macAddr=results["interface"]["macAddr"],
        isVpn=results["interface"]["isVpn"],
        externalIp=results["interface"]["externalIp"]).set(1)
    server.labels(id=results["server"]["id"],
        name=results["server"]["name"],
        location=results["server"]["location"],
        country=results["server"]["country"],
        host=results["server"]["host"],
        port=results["server"]["port"],
        ip=results["server"]["ip"]).set(1)
    downloadBandwidth.set(results["download"]["bandwidth"])
    downloadBytes.set(results["download"]["bytes"])
    downloadElapsed.set(results["download"]["elapsed"]/1000)
    uploadBandwidth.set(results["upload"]["bandwidth"])
    uploadBytes.set(results["upload"]["bytes"])
    uploadElapsed.set(results["upload"]["elapsed"]/1000)


if __name__ == '__main__':

    start_http_server(config["port"])
    printLog(f"Startup delay...waiting {config['delay']}")
    time.sleep(config["delay"])
    while True:
        updateValues(runSpeedTest())
        printLog(f"Waiting for next run...waiting {config['interval']}")
        time.sleep(config["interval"])
