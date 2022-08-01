# TiDAL 3D

A 3D renderer for the EMF 2022 badge.

It can render objects from Wavefront OBJ/MTL files, such as you might export from Blender, and crudely supports features like back-face culling, frustum culling, directional lighting, material colours, and flat shading.

Here's a quick demo showing the obligatory Cube (a platonic solid) and Utah Teapot (a plate-onic solid):

https://user-images.githubusercontent.com/597661/182123844-fca92232-0b1e-4d91-830c-54877b67a679.mp4

## Trying It Out

The app is in the hatchery/app store, but ⚠️  PLEASE NOTE ⚠️  that it does require a custom build of the firmware to function.

The customisations to the firmware include some additional framebuffer routines for drawing polygons and a native module containing some commonly used 3D maths functions. Only with these fast native implementations can we acheive such high framerate in the renderer app.

You can build the customised firmware from my branch of the TiDAL-Firmware repo using the instructions below.

**Step 1:**

Get and setup the Espressif ESP32 toolchain:

```
$ git clone -b release/v4.4 --recurse-submodules https://github.com/espressif/esp-idf
$ ./esp-idf/install.sh
```

**Step 2:**

Get and build the firmware:

```
$ git clone -b mbooth-tidal3d --recurse-submodules https://github.com/mbooth101/TiDAL-Firmware
$ ./TiDAL-Firmware/firmware_build.sh
```

**Step 3:**

Force the badge into download mode by holding down the **bootloader** button whilst pressing the **reset** button. The screen will be go blank. Now you can deploy the firmware:

```
$ ./TiDAL-Firmware/firmware_deploy.sh
```

Press the **reset** button once again to boot the badge back into the main menu.

**Step 4:**

Install the app from the hatchery/app store as normal. [Click to view the app in the hatchery](https://2022.badge.emfcamp.org/projects/tidal_3d/).

Alternatively, clone this repository and use the upload script to install the app over USB serial:

```
$ sudo dnf install minicom python3-pyserial # Fedora only command
$ sudo apt install minicom python3-serial   # Ubuntu only command
$ git clone https://github.com/mbooth101/tidal3d
$ cd tidal3d
$ ./upload.sh
```
