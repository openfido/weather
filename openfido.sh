#!/bin/python3
import os, sys, shutil

OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

try:

    CSVFILE="weather.csv"
    GLMFILE="weather.glm"
    LATLON=[37.4,-122.2]
    YEARS=[2020]
    NAME="test"
    BRANCH="develop"

    os.system(f"curl -sL https://raw.githubusercontent.com/openfido/weather/{BRANCH}/__init__.py > weather.py")

    import weather

    os.chdir("/tmp")

    outputs = [CSVFILE,GLMFILE]

    weather.main([],outputs,{"year":YEARS,"position":LATLON,"name":NAME})

    for RESULT in outputs:
        shutil.copyfile(RESULT,OPENFIDO_OUTPUT)

