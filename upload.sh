#!/bin/sh

# Copy files onto the device using the pyboard tool from micropython,
# reproduced in this repo for convenience so we don't have to have
# a local clone available of the firmware or micropython repos:
# https://github.com/micropython/micropython/blob/master/tools/pyboard.py
if [ -z "$1" ] ; then
	for f in *.py *.obj *.mtl ; do
		python tools/pyboard.py \
			--no-soft-reset -d /dev/ttyACM0 -f cp $f :/apps/TiDAL3D/$f
	done
else
	python tools/pyboard.py \
		--no-soft-reset -d /dev/ttyACM0 -f cp $1 :/apps/TiDAL3D/$1
fi

# Monitor serial console
minicom -D /dev/ttyACM0
