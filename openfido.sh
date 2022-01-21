#!/bin/sh
#
# Generic python environment for OpenFIDO
#

on_error()
{
    echo '*** ABNORMAL TERMINATION ***'
    echo 'See error Console Output stderr for details.'
}

trap on_error 1 2 3 4 6 7 8 11 13 14 15

set -x # print commands
set -e # exit on error
set -u # nounset enabled

export DEBIAN_FRONTEND=noninteractive
apt-get -q -y update > /dev/null
apt-get -q -y install python3 python3-pip > /dev/null
python3 -m pip install -q -r requirements.txt > /dev/null

python3 openfido.py || on_error
