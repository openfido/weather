#!/bin/sh

set -e # print commands
set -x # exit on error
set -u # nounset enabled

apt update -y
apt install python3 -q -y
/usr/bin/python3 openfido.py
