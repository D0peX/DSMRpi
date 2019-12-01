# DSMRpi 

Small script for reading serial data from a DSMR energy meter. With influxDB backend.

## Preface
Since I had a spare Raspberry Pi (Model B+) and a DSMR energy meter. I figured i could as well read all the data it is sending to its P1 port. However. There was a catch. Other projects aimed at reading energy data from their meters involved either a newer model Pi, or were not capable of high precision, or both.

The goal was to create something that can read and store the data efficiently, while maintaining high precision.

### What it does
Reads all of the following:
* Gas usage total
* Power used from the grid, and sent back to the grid
* Power usage totals for tariff 1 and 2.
* Actual power usage 
* Voltage reading
* Aperage

**With a fixed interval of 1 second!** 

## Requirements
* **Separate server with InifluxDB** (mandatory). Graphing can be done in Grafana.
> I would not reccomend InfluxDB on a Pi. This would destroy the SD card. Also, i have not tested it on my Pi. I have little to no CPU headroom left on mine.

> According to my calculation; storing this information for 1 year, will take approx. 2GB disk space for the DB. You will have to create your own retention policy on InfluxDB, if you dont want to have 1s precision down the line.

* Raspberry Pi (tested on model B+ 2014)
    1. Headless (script is CPU intensive - Easiliy 50%-70%)
    1. Set-up with Debian preferred and up-to-date
    1. Timezone set, NTP prefferd
    1. Python3
    1. Serial->USB cable connected to DSMR (P1 cable)
    1. Ethernet connected

## How-to use
Set-up your Raspberry accordingly. You want your raspberry to be headless. **This script CPU hungry.**

1. git clone the file to your raspberry pi.
    * Either use `git clone` or move it to ~/DSMRpi.
Make sure that `app.py` and such are inside this directory.
1. Set up python: `pip install requests pyserial` 
1. Set up the config file: `cp example.config.py config.py`
    * Make sure to edit `config.py` afterwards. Edit your settings accordingly.
1. Make `app.py` executable `chmod +x app.py`
1. Create a systemd unit file: `sudo cp systemd.unit /lib/systemd/system/DSMRpi.service`
1. Enable the service
    ```
    sudo systemctl daemon-reload 
    sudo systemctl enable DSMRpi
    sudo systemctl start DSMRpi
    sudo systemctl status DSMRpi
    ```

If you have any errors here, please check your settings. Else open an issue on github if you suspect the error to be in the script. Even better: Create a pull request with a fix.

### ToDo's
* Fix time reading from the meter
>In my case, the time on my DSMR is lagging by ~2 minutes.
* Add in reading power Fail logs (`timeConv` function is already there)
* More?

## Honorable mentions

I have had to use many resources to get this working honestly. So here are some links to guides / information i have used:
* GeJanssen's blog (Dutch) - [link](http://gejanssen.com/howto/Slimme-meter-uitlezen/)
* DSMR5 spec sheet (hosted on GeJanssen) - [link (pdf is ENG)](http://gejanssen.com/howto/Slimme-meter-uitlezen/Slimme_meter_ESMR50.pdf) 
* InfluxDB write API - [link](https://docs.influxdata.com/influxdb/v1.7/tools/api/)
* InfluxDB Line Protocol - [link](https://docs.influxdata.com/influxdb/v1.7/write_protocols/line_protocol_reference/)
