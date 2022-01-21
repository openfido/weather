#!/bin/python3

import os, sys, shutil

sys.path.append(".")

import __init__ as weather

OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

CSVFILE="weather.csv"
GLMFILE="weather.glm"
LATLON=[37.4,-122.2]
YEARS=[2020]
NAME="test"
BRANCH="develop"

os.chdir("/tmp")

outputs = [CSVFILE,GLMFILE]

weather.main([],outputs,{"year":YEARS,"position":LATLON,"name":NAME})

for RESULT in outputs:
    shutil.copyfile(RESULT,OPENFIDO_OUTPUT)

