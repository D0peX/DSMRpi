# DSMRpi 
Read data from an DSMR meter over serial with an Raspberry Pi.

This script will read data from your utility meter, including gas, each second.
These operation are fairly write intensive. With this in mind, i'm using InfluxDB on another host to send data to.
SD cards are NOT suitable for this workload. You need an other host to write data to!

The data can then be viewed in Grafana.

This script is written according DSMR5 'standards'.

## How-to use
todo