#!/bin/bash

set -x # print commands
set -e # exit on error
set -u # nounset enable

function on_error()
{
    echo "*** ABNORMAL TERMINATION ***"
    echo "See error console output for details."
}

trap "on_error" ERR

TMPDIR=/tmp/nsrdb_weather
mkdir -p ${TMPDIR}
cd ${TMPDIR}

cp -r $OPENFIDO_INPUT/* .

CSVFILE="weather.csv"
GLMFILE="weather.glm"
LATLON="37.4,-122.2"
YEAR="2020"

gridlabd nsrdb_weather -y=${YEAR} -p=${LATLON} -c=${CSVFILE} -g=${GLMFILE}

cp ${TMPDIR}/* ${OPENFIDO_OUTPUT}
