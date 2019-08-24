# Settings for app.py
#
# Edit your settings here

confSerial = dict (
    baudrate = 115200,
    port = "/dev/ttyUSB0",
)

# set influxDB host
database = dict (
    host = "10.10.30.55",
    password = "",
    port = "8086",
    db = "testmeter",

)

# Set your timezone according to this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
timezone = dict (
    tz = "Europe/Amsterdam"
)