"""weather pipeline

INPUTS

    config.csv (required)

OUTPUTS

    CSVFILE

    GLMFILE

ENVIRONMENT

    OPENFIDO_INPUT

    OPENFIDO_OUTPUT

CONFIGURATION

    CSVFILE,filename.csv
    GLMFILE,filename.glm
    NAME,objectname
    EMAIL,your.email@your.org
    APIKEY,your-api-key
    YEARS,year1,year2,...
    LATLON,latitude,longitude

"""

import os, sys, shutil, json, csv

OPENFIDO_INPUT = os.getenv("OPENFIDO_INPUT")
OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

try:
    with open(f"{OPENFIDO_INPUT}/config.csv","r") as f:
        reader = csv.reader(f)
        for line in reader:
            if len(line) == 1:
                globals()[line[0]] = True
            elif len(line) == 2:
                globals()[line[0]] = line[1]
            elif len(line) > 2:
                globals()[line[0]] = line[1:]
except Exception as err:
    print("ERROR: {err}, see output for an example config.csv",file=sys.stderr)
    shutil.copyfile("example/config.csv",f"{OPENFIDO_OUTPUT}/config.csv")
    exit(1)

os.chdir("/tmp")

sys.path.append(".")
import __init__ as weather

weather.email = EMAIL
weather.addkey(APIKEY)
outputs = [CSVFILE,GLMFILE]

weather.main([],outputs,{"year":YEARS,"position":LATLON,"name":NAME})

for file in outputs:
    shutil.copyfile(file,f"{OPENFIDO_OUTPUT}/{file}")

