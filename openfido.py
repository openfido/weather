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

sys.path.append(".")

import __init__ as weather

OPENFIDO_INPUT = os.getenv("OPENFIDO_INPUT")

with open(f"{OPENFIDO_INPUT}/config.csv") as f:
    reader = csv.reader(f)
    for line in reader:
        globals()[line[0]] = line[1:]

OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

os.chdir("/tmp")

weather.email = EMAIL
weather.addkey(APIKEY)
outputs = [CSVFILE[0],GLMFILE[0]]

weather.main([],outputs,{"year":YEARS,"position":LATLON,"name":NAME[0]})

for RESULT in outputs:
    shutil.copyfile(RESULT,OPENFIDO_OUTPUT)

