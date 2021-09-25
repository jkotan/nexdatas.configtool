#!/usr/bin/env bash

if [ "$1" = "2" ]; then
    echo "run python-nxsconfigserver tests"
    docker exec  ndts python test
else
    echo "run python3-nxsconfigserver tests"
    docker exec  ndts python3 test
fi
if [ "$?" -ne "0" ]; then exit 255; fi
