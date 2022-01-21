#!/bin/sh

set -e # print commands
set -x # exit on error
set -u # nounset enabled

apt-get update -y > /dev/stderr
apt-get install python3 -q -y > /dev/stderr

echo "Running in $PWD..." 
ls $PWD

/usr/bin/python3 openfido.py
