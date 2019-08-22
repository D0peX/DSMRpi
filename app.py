#!/bin/python3

import serial
import re
import datetime
from config import confSerial, database
import requests

# Default configuration for DSMR 5.0
scon = serial.Serial()
scon.port = "/dev/ttyUSB0"
scon.baudrate = 115200
scon.ByteSize = serial.EIGHTBITS
scon.parity = serial.PARITY_NONE
scon.stopbits = serial.STOPBITS_ONE
scon.xonxoff = 0
scon.rtscts = 0
scon.timeout = 2

SIZE = 26 # number of lines returned by DSMR per telegram
data = []
reMatch = re.compile("\(.*?\)") # This RE is used to match data between `()`

    
def timeConv(data):
    """Expects `data` as string. Returns string with UNIX time UTC"""

    matches = re.findall(reMatch, data)
    bad = "(S)"
    if len(matches):
        t = matches[0].strip(bad)
        date = datetime.datetime.strptime(t, "%y%m%d%H%M%S")
        date = date.replace(tzinfo=datetime.timezone.utc).timestamp()
        #date = str(date).rstrip(".0")
        date = int(date)
        print(date)
        return(date)

def equipmentConv(data):
        matches = re.findall(reMatch, data)

        bad = "()"
        if len(matches):
                s = matches[0].strip(bad)
                return(s)   

def kwhConv(data):
    """Expects `data` as string. Returns a `float`"""

    matches = re.findall(reMatch, data)
    bad = "(*kWh)"
    if len(matches):
        k = matches[0].strip(bad)
        k = k.lstrip("0")
        return(float(k))

def tariffConv(data):
        matches = re.findall(reMatch, data)

        bad = "()"
        if len(matches):
                t = matches[0].strip(bad)
                t = t.lstrip("0")
                return(int(t))  

def gasConv(data):
    """Expects `data` as string. Returns a `float`"""
    matches = re.findall(reMatch, data)
    bad = "(*m3)" 
    if len(matches):
        time = timeConv(matches[0])
        gas = matches[1].strip(bad)
        return(time,gas)

def postData(data):
        """Function expects `data` as follows:
        `'energy,tariff1=value,tariff2=value timestamp'`
        Databse config is in `config.py`"""

        try:
                response = requests.post("http://{}:{}/write?db={}".format(database["host"],database['port'],database["db"]),data=data)
                if response.status_code == 204:
                        return
        except requests.ConnectionError as e:
                print("[Error] Connection to InfluxDB failed: {}".format(e))
        else:
                print("[Error] InfluxDB did not accept the data: {}".format(response.status_code))
                print(response.content)

#
#
# Opening connection to serial
try:
    scon.open()
    while True:
        data.append(str(scon.readline()))
        if len(data) == 26:
            
            #send basic data to influx
            timestamp = timeConv(data[4])
            id = equipmentConv(data[5])
            t1 = kwhConv(data[6])
            postData("tariff1,equipment_id={} value={} {}".format(id,t1,timestamp))
            t2 = kwhConv(data[7])
            postData("tariff2,equipment_id={} value={} {}".format(id,t2,timestamp))
            actual = kwhConv(data[11])
            postData("actual_power_down,equipment_id={} value={} {}".format(id,actual,timestamp))
            tariff = tariffConv(data[10])

            # Hier gaat wat fout.
            # ik post (id,tariff,timestamp)
            # influx wilt [tag],[value],[timestamp] weten. Al mijn tags zijn equipment ID
            # zie: https://v2.docs.influxdata.com/v2.0/write-data/
            # tariff1,equipment_id=4530303437303030303234363436393138 value=2603.84 1566510608"
            postData("tariff_indicator,equipment_id={} value={} {}".format(id,tariff,timestamp))

            #empty list
            del data[:]

    
except serial.SerialException as e:
    print("[Error] :: {}\n").format(e)
    
## END