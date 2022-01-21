#!/bin/sh

set -e # print commands
set -x # exit on error
set -u # nounset enabled

apt-get update -y
apt-get install python3 -q -y

echo "Running in $PWD"
/usr/bin/python3 openfido.py
