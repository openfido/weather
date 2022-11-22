#!/bin/sh
#
# Generic python environment for OpenFIDO
#

on_error()
{
    echo '*** ABNORMAL TERMINATION ***'
    echo 'See error Console Output stderr for details.'
    exit 1
}

trap on_error 1 2 3 4 6 7 8 11 13 14 15

set -x # print commands
set -e # exit on error
set -u # nounset enabled

LATITUDE=$(grep '^LATITUDE,' ${OPENFIDO_INPUT}/config.csv | cut -f2 -d,)
LONGITUDE=$(grep '^LONGITUDE,' ${OPENFIDO_INPUT}/config.csv | cut -f2 -d,)
BASENAME=$(grep '^BASENAME,' ${OPENFIDO_INPUT}/config.csv | cut -f2 -d,)
YEAR=$(grep '^YEAR,' ${OPENFIDO_INPUT}/config.csv | cut -f2 -d,)

cd "${OPENFIDO_OUTPUT}"
if [ -z "${YEAR}" ]; then
    /usr/local/bin/gridlabd noaa_forecast -p="${LATITUDE},${LONGITUDE}" -c="${BASENAME}.csv" -g="${BASENAME}.glm" -n="${BASENAME}"
else
    /usr/local/bin/gridlabd nsrdb_weather -y="${YEAR}" -p="${LATITUDE},${LONGITUDE}" -c="${BASENAME}.csv" -g="${BASENAME}.glm" -n="${BASENAME}"
fi