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

TMPDIR=/tmp/weather_$$
rm -rf ${TMPDIR}
mkdir -p ${TMPDIR}
cd ${TMPDIR}

CSVFILE="weather.csv"
GLMFILE="weather.glm"
LATLON="37.4,-122.2"
YEAR="2020"
NAME="test"
BRANCH="develop"

curl -sL https://raw.githubusercontent.com/openfido/weather/${BRANCH}/__init__.py > weather.py

python3 weather.py -y=${YEAR} -p=${LATLON} -n=${NAME} -c=${CSVFILE} -g=${GLMFILE}

cp ${TMPDIR}/{${CSVFILE},${GLMFILE}} ${OPENFIDO_OUTPUT}

rm -rf ${TMPDIR}
