#!/bin/python3

import serial
import re
import datetime
import pytz
import requests
from config import confSerial, database, timezone, objects

# Default configuration for DSMR 5.0
scon = serial.Serial()
scon.port = confSerial["port"]
scon.baudrate = confSerial["baudrate"]
scon.ByteSize = serial.EIGHTBITS
scon.parity = serial.PARITY_NONE
scon.stopbits = serial.STOPBITS_ONE
scon.xonxoff = 0
scon.rtscts = 0
scon.timeout = 2

data = []
reMatch = re.compile("(\d{3,}\.\d*|\d{3,}|\d{2}\.\d{3,})")  # This RE is used to match data between `()`

def timeConv(data):
    """Expects `data` as string. Returns string with UNIX time UTC"""
    # Messing with timeConv might result in influx not liking your date/time. beware.

    matches = re.findall(reMatch, data)
    
    if len(matches):
        t = matches[0]
        tz = pytz.timezone(timezone['tz'])
        # format string read from meter output
        date = datetime.datetime.strptime(t, "%y%m%d%H%M%S")
        # convert local time read from meter, to UTC time
        local_dt = tz.localize(date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        date = int(utc_dt.timestamp())  # convert to unix

        return(date)

def floatConv(data):
    """Expects `data` as string. Returns a `float`"""

    matches = re.findall(reMatch, data)
    if len(matches):
        k = matches[0]
        k = k.lstrip("0") # Need to strip all leading zero's. Otherwise it cannot be converted to float.
        return(float(k))

def intConv(data):
    matches = re.findall(reMatch, data)

    if len(matches):
        t = matches[0]
        t = t.lstrip("0") # Need to strip all leading zero's. Otherwise it cannot be converted to int.
        t = t.rstrip(".0") # trailing '.0' can only be stripped from volt and amps
        return(int(t))

def gasConv(data):
    """Expects `data` as string. Returns a `float`"""
    matches = re.findall(reMatch, data)
    if len(matches):
        #time = timeConv(matches[0]) # Time returned here is only upated every 5 minutes according to DSMR standard
        gas = matches[1]
        return(gas)

def postData(data):
    """Function expects `data` as follows:
    `'energy,tariff1=value,tariff2=value timestamp'`
    Databse config is in `config.py`"""

    try:
        response = requests.post("http://{}:{}/write?db={}&precision=s".format(
            database["host"], database['port'], database["db"]), data=data)
        if response.status_code == 204:
            return
    except requests.ConnectionError as e:
        print("[DSMRpi ERROR] Connection to InfluxDB failed: {}".format(e))
    else:
        print("[DSMRpi ERROR] InfluxDB did not accept the data: {}".format(response.status_code))
        print(response.content)

#
#
# Opening connection to serial

firstloop = True
try:
    scon.open()
    _ = scon.readline() # first line of output is "b'\x00\n'". and not needed.
    print("[DSMRpi INFO] Successfully opened serial connection on {c}.\nWriting data to: {i}:{p} DB:{d}".format(c=confSerial['port'], i=database['host'], p=database['port'], d=database['db']))
    while True:
        line = str(scon.readline())
        if "!" not in line:
                # read data until '!' is returned in scon.readline
                # Once `!` is seen in `line`, it will defer to the else statement
                data.append(line)

        elif firstloop == False:
            # Looping over all lines in data. Figuring out all the bits and pieces.
            for i in data:
                if objects['timestamp'] in i:    
                    timestamp = timeConv(i)
                elif objects['tariff1down'] in i:
                    tariff1= floatConv(i)
                elif objects['tariff2down'] in i:
                    tariff2 = floatConv(i)
                elif objects['powerused'] in i:
                    powerused = floatConv(i)
                elif objects['powersent'] in i:
                    powersent = floatConv(i)
                elif objects['gas'] in i:
                    gas = gasConv(i)
                elif objects['tariffindicator'] in i:
                    tinc = intConv(i)
                elif objects['voltageL1'] in i:
                    vl1 = intConv(i)
                elif objects['currentL1'] in i:
                    cl1 = intConv(i)
                #TODO power failure logging
                # elif objects['powerfails'] in i:
                #     pass
                # elif objects['longpowerf'] in i:
                #     pass
            
            # Create the string to pass to influxDB
            # according to https://docs.influxdata.com/influxdb/v1.7/guides/writing_data/
            s = """tariff1,tariffindicator={tinc} value={t1} {ts}
tariff2,tariffindicator={tinc} value={t2} {ts}
powerused,tariffindicator={tinc} value={pu} {ts}
powersent,tariffindicator={tinc} value={ps} {ts}
gas,tariffindicator={tinc} value={gas} {ts}
voltageL1,tariffindicator={tinc} value={vl1} {ts}
currentL1,tariffindicator={tinc} value={cl1} {ts}""".format(tinc=tinc, ts=timestamp, t1=tariff1, t2=tariff2, pu=powerused, ps=powersent, gas=gas, vl1=vl1, cl1=cl1)
            
            postData(s)
            # cleanup
            data.clear()

        else:
            # do nothing, and set firstloop to False
            firstloop = False
            print("[DSMRpi INFO] Starting to send data now. No further output expected.")
            data.clear()        

except serial.SerialException as e:
    print("[DSMRpi ERROR] {}\n").format(e)

# END
