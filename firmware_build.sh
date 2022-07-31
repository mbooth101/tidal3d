#!/bin/bash
set -e -o pipefail

SCRIPT_DIR=$(cd $(dirname $0) && pwd)
TIDAL_DIR=$SCRIPT_DIR/../TiDAL-Firmware

source ../esp-idf/export.sh

set -x

export IOT_SOLUTION_PATH=$TIDAL_DIR/esp-iot-solution
export V=1

pushd $TIDAL_DIR
./scripts/firstTime.sh

pushd micropython
make -C mpy-cross

pushd ports/esp32
(cd boards && ln -sfn $TIDAL_DIR/tildamk6 ./tildamk6)

make submodules BOARD=tildamk6 USER_C_MODULES=$TIDAL_DIR/drivers/micropython.cmake
make BOARD=tildamk6 USER_C_MODULES=$TIDAL_DIR/drivers/micropython.cmake clean all
popd
popd
popd
