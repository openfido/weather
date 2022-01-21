#!/bin/sh

function on_error()
{
    echo "*** ABNORMAL TERMINATION ***"
    echo "See error console output for details."
}

trap "on_error" ERR

set -e # print commands
set -x # exit on error
set -u # nounset enabled

apt-get -q -y update > /dev/null
apt-get -q -y install python3 python3-pip > /dev/null
python3 -m pip install -q -r requirements.txt > /dev/null

python3 openfido.py
