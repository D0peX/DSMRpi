#!/bin/sh
# Small script that copies current working dir to remote host

HOST="meterkast"
USER="pi"
DEST="/home/pi/dsmr"
DIR=$(pwd)

echo "Moving files to Pi..."
echo `scp -r "${DIR}" "${USER}"@"${HOST}":"${DEST}"`
echo "Done"
