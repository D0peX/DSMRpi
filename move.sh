#!/bin/sh
# Small script that copies current working dir to remote host

HOST="10.10.30.54"
USER="pi"
DEST="/home/pi/dsmr"
DIR=$(pwd)

echo "Moving files to Pi..."
echo `scp -r "${DIR}" "${USER}"@"${HOST}":"${DEST}"`
echo "Done"