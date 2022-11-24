# YAW1F5 remote

This module enables you to control a Gree Aircondition unit that get shipped with YAW1F5 remote control over infrared using RP2040 and Micropython. According to web research there are other variants like YAW1F or YAW1F2 which are *potentially* compatible too, but I cannot state this from personal experience. Also other vendors seem to resell the Gree units under different brand names.

I could not find anywhere an alternative, so want to share it here to make it available to everybody for their own use.

I personally used this module to build a MQTT to Aircondition unit compatible with Homeassistants HVAC_MQTT using this module.

remotePy unit is used, which can be found at: https://github.com/meloncookie/RemotePy  (credits to meloncookie!)
Note: I adjusted the UpyIrTx.py unit a bit to get a 38 kHz carrier out. Not sure if this is due to the remotePy code, or the MicroPython release used, but it fixed it for my 1.19 version of MicroPython - following issue report https://github.com/meloncookie/RemotePy/issues/4 might answer.

# HW

Connect to GPIO19 a normal transistor/fet circuit and IR diode.

Note that the GPIO current setting with RP2040 and Micropython is too low to connect directly an IR diode with resistor, the range is too short to be useful.

# Usage
Upload all files to your RP2040 (Raspberry Pi Pico - I use it with the wireless variant).

## Initialization
```
import YAW1F5 as ir;
ir.init(); 
```

Afterwards settings can be changed using functions like:

```
ir.setMode('cool')
ir.setFan('low')
ir.setPreset('activity')
ir.setSwing('on')
ir.setTemperature(22) # Unit is Celsius, not strange things like Fahrenheit or Kelvin :-)
```
Changing those settings does not yet transmit the new state to the device

When calling ```ir.send()``` function, the new settings will be transmitted wireless over the infrared diode connected to pin GPIO19.

The power can be directly taken from the 4 pin Wifi connector within the Gree unit. The outer 2 pins deliver 5V, which can be directly connected to a USB cable to plug it into the RP2020 module.

Happy hacking!
