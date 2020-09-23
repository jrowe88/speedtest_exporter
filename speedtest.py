###############################################################################
# speedtest.py
# copyright Jim Rowe (2020)
###############################################################################
#  Perform a internet speed test using SpeedTest cli
#  Report results using the prometheus python client
#  Some parameters set from the system environment:
#     PORT - port for reporing metrics
#     STARTUPDELAY_SECONDS - delay in seconds for running speedtest after startup (default =  15 seconds)
#     INTERVAL_SECONDS - interval in sectinos between speedtest (default = 3600 seconds)
###############################################################################

from prometheus_client import (Gauge, start_http_server)
from prometheus_client.twisted import MetricsResource
import time, os, subprocess, json, threading
from datetime import datetime
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import (reactor, task)
from indexResource import IndexResource

def printLog(entry: str):    
    print(f"{datetime.now()} - {entry}")

loopFailed = False
printLog("Speedtest exporter started.")

#setup run parameters
config = {'port': 9497,
        'interval': 1800,
        'delay': 30}

if os.getenv("PORT") != None:
    config["port"] = int(os.getenv("PORT"))

if os.getenv("INTERVAL_SECONDS") != None:
    config["interval"] = int(os.getenv("INTERVAL_SECONDS"))

if os.getenv("STARTUPDELAY_SECONDS") != None:
    config["delay"] = int(os.getenv("STARTUPDELAY_SECONDS"))

printLog(f'exporter port={config["port"]}')
printLog(f'startup delay={config["delay"]}s')
printLog(f'interval={config["interval"]}s')

#create metrics
ts = Gauge('speedtest_timestamp', 'Timestamp of the speedtest in Unix time.')
jitter = Gauge('speedtest_ping_jitter_seconds','Ping jitter in seconds.')
latency = Gauge('speedtest_ping_latency_seconds', 'Ping latency in seconds.')
packetloss = Gauge('speedtest_packet_loss', 'Packet loss during speed test.')
testinfo = Gauge('speedtest_test_info','Information about the server, isp, and interface used for the test, value is unix timestamp of the test.',
    ['internalIp','interfaceName','macAddr','isVpn','externalIp','id','serverName','location','country','host','port','ip','isp'])
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
    results = complete.stdout
    printLog(results)
    return json.loads(results)

#Update the metric values
def updateValues(results: json):
    printLog("Updating values")
    tsValue = datetime.strptime(results["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
    ts.set(tsValue.timestamp())
    jitter.set(results["ping"]["jitter"]/1000)
    latency.set(results["ping"]["latency"]/1000)
    packetloss.set(results.get("packetLoss",0))    
    testinfo.labels(internalIp=results["interface"]["internalIp"],
        interfaceName=results["interface"]["name"],         
        macAddr=results["interface"]["macAddr"],
        isVpn=results["interface"]["isVpn"],
        externalIp=results["interface"]["externalIp"],
        id=results["server"]["id"],
        serverName=results["server"]["name"],
        location=results["server"]["location"],
        country=results["server"]["country"],
        host=results["server"]["host"],
        port=results["server"]["port"],
        ip=results["server"]["ip"],
        isp=results["isp"]).set(tsValue.timestamp())
    downloadBandwidth.set(results["download"]["bandwidth"])
    downloadBytes.set(results["download"]["bytes"])
    downloadElapsed.set(results["download"]["elapsed"]/1000)
    uploadBandwidth.set(results["upload"]["bandwidth"])
    uploadBytes.set(results["upload"]["bytes"])
    uploadElapsed.set(results["upload"]["elapsed"]/1000)

def checkInternetSpeed():
    updateValues(runSpeedTest())        
    printLog(f"Waiting for next run...waiting {config['interval']}")
        
def speedTestLoopFailed(failure):
    print(failure.getBriefTraceback())
    loopFailed = True
    if reactor.running:
        reactor.stop()

#Service execution
if __name__ == '__main__':
    
    #pause
    printLog(f"Startup delay...waiting {config['delay']}")
    time.sleep(config["delay"])

    #setup twisted web server
    root = Resource()
    root.putChild(b'', IndexResource())
    root.putChild(b'metrics', MetricsResource())
    factory = Site(root)    
    reactor.listenTCP(int(config["port"]), factory)       

    #setup and run speedtest loop
    loop = task.LoopingCall(checkInternetSpeed)
    ld = loop.start(config["interval"])
    ld.addErrback(speedTestLoopFailed)
    
    #start the webserver and reactor loop
    if not loopFailed:
        printLog(f"Starting exporter on <server>:{config['port']}/metrics")
        reactor.run()
