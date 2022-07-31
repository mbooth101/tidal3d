#!/bin/bash
set -e -o pipefail

SCRIPT_DIR=$(cd $(dirname $0) && pwd)
TIDAL_DIR=$SCRIPT_DIR/../TiDAL-Firmware

source ../esp-idf/export.sh

set -x

pushd $TIDAL_DIR/micropython/ports/esp32

python ../../../../esp-idf/components/esptool_py/esptool/esptool.py -p /dev/ttyACM0 -b 460800 --before default_reset --after no_reset --chip esp32s3  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 build-tildamk6/bootloader/bootloader.bin 0x8000 build-tildamk6/partition_table/partition-table.bin 0xd000 build-tildamk6/ota_data_initial.bin 0x10000 build-tildamk6/micropython.bin

popd
