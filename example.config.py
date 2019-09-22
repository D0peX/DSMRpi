# Settings for app.py
#
# Edit your settings here

confSerial = dict (
    baudrate = 115200,
    port = "/dev/ttyUSB0",
)

# set influxDB host
database = dict (
    host =      "",
    password =  "",
    port =      "",
    db =        "",

)

timezone = dict (
    # Set your timezone according to this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    tz = "Europe/Amsterdam"
)

objects = dict (
    # `objects` used for picking correct values when looping over the `data` list.
    timestamp =     "0-0:1.0.0",
    equipmentID =   "0-0:96.1.1",
    tariff1down =   "1-0:1.8.1",
    tariff2down =   "1-0:1.8.2",
    tariff1sent =   "1-0:2.8.1",
    tariff2sent =   "1-0:2.8.2",
    powerused =     "1-0:1.7.0",
    powersent =     "1-0:2.7.0",
    gas =           "0-1:24.2.1",
    tariffindicator = "0-0:96.14.0",
    voltageL1 =     "1-0:32.7.0",
    currentL1 =     "1-0:31.7.0",
    powerfails =    "0-0:96.7.21",
    longpowerf =    "0-0:96.7.9",

)