#!/bin/sh

APP_DIR=/apps/tidal_3d

# Copy files onto the device using the pyboard tool from micropython,
# reproduced in this repo for convenience so we don't have to have
# a local clone available of the firmware or micropython repos:
# https://github.com/micropython/micropython/blob/master/tools/pyboard.py
python tools/pyboard.py --no-soft-reset -d /dev/ttyACM0 -f mkdir $APP_DIR >/dev/null
APP_FILES="$@"
if [ -z "$APP_FILES" ] ; then
	APP_FILES="app/*.py app/*.obj app/*.mtl"
fi
for f in $APP_FILES ; do
	python tools/pyboard.py --no-soft-reset -d /dev/ttyACM0 -f cp $f :$APP_DIR/$(basename $f)
done

# Monitor serial console
minicom -D /dev/ttyACM0
