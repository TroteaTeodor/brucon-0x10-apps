## Brucon 0x10 badge games by Ko-Lab makerspace
This repository contains uPython games for the Brucon 2024 badge

## How to install all apps
There is a python script that will look for new devices that are connected after the script has started up and will then automatically flash all apps to it. It works on mac an linux. To use follow these steps:

- install mpremote: `pip3 install mpremote`
- run `python3 install.py`
  - Important: make sure your device is not connected yet when you start this script
- connect your device now
- wait until the script is not doing any anymore
- now kill the script and press B button on the badge.
  
## If your badge is not working
Then try to flash it with the web flasher at https://onemorething.curious.supplies/ (needs chrome or edge)
To get it into bootloader mode,
first turn of the badge by pressing B twice, then press and hold the little white buttons back of the badge while plugging in the USB cable.

## Credits
Credits to https://hatchery.badge.team/projects/matrix_letter_rain for the icon.py file
