#!/bin/sh

set -e # print commands
set -x # exit on error
set -u # nounset enabled

apt-get update -y > /dev/stderr
apt-get install python3 python3-pip -q -y > /dev/stderr
python3 -m pip install requests -q

python3 openfido.py
