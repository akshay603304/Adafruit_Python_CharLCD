'''
Adafruit compatible using CharLCD class to represent a character LCD attached
to a PCF8574/A I2C IO expander
Copyright (C) 2015 Sylvan Butler

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''


import Adafruit_GPIO.PCF8574 as IOX
import Adafruit_CharLCD as ALCD

# the PCF8574 is a transparent I2C GPIO expander, meaning a write to the PCF
# directly maps to the PCF outputs (and a read from the inputs, unused here)
#
# PCF8574 pins 4-7 and 9-12 are bits 0-3 and 4-7, respectively
#
# Char LCD pin to I/O expander GPIO pin number maps
# LCD pin name: PCF port bit
PINMAPS = [
{
# map0 - DFRobot, YwRobot, Sainsmart?, also generic black PCB
# http://www.dfrobot.com/image/data/DFR0175/I2C%20LCD%20Backpack%20schematic.pdf
'PCF_RS': 0,
'PCF_RW': 1,
'PCF_EN': 2,
'PCF_BL': 3,
'PCF_D4': 4,
'PCF_D5': 5,
'PCF_D6': 6,
'PCF_D7': 7,
}, {
# map1 - map0 with nibbles swapped, generic green PCB
'PCF_RS': 4,
'PCF_RW': 5,
'PCF_EN': 6,
'PCF_BL': 7,
'PCF_D4': 0,
'PCF_D5': 1,
'PCF_D6': 2,
'PCF_D7': 3,
}, {
# map2 - mjkdz board w/22 turn trimmer, GY-LCD-V1
'PCF_RS': 6,
'PCF_RW': 5,
'PCF_EN': 4,
'PCF_BL': 7,
'PCF_D4': 0,
'PCF_D5': 1,
'PCF_D6': 2,
'PCF_D7': 3,
}, {
# map3 - map2 with nibbles swapped
'PCF_RS': 0,
'PCF_RW': 1,
'PCF_EN': 2,
'PCF_BL': 3,
'PCF_D4': 6,
'PCF_D5': 5,
'PCF_D6': 4,
'PCF_D7': 7,
}, {
# map4 - from some found arduino code with no board description
'PCF_RS': 4,
'PCF_RW': 5,
'PCF_EN': 6,
'PCF_BL': 7,
'PCF_D4': 2,
'PCF_D5': 1,
'PCF_D6': 0,
'PCF_D7': 3,
},
]

# Typical LCD pinout:
# 01 - LCD_VSS - GND
# 02 - LCD_VDD - VCC, +5v
# 03 - LCD_VO - Contrast in (10k POT VSS to VDD)
# 04 - LCD_RS
# 05 - LCD_RW - High to read data from LCD
# 06 - LCD_EN
# 07 - LCD_D0 - N/C in 4bit mode
# 08 - LCD_D1 - N/C in 4bit mode
# 09 - LCD_D2 - N/C in 4bit mode
# 10 - LCD_D3 - N/C in 4bit mode
# 11 - LCD_D4
# 12 - LCD_D5
# 13 - LCD_D6
# 14 - LCD_D7
# 15 - LCD_BLA - Backlight Anode (+)
# 16 - LCD_BLC - Backlight Cathode (-)
# w/RGB backlight, replace 16 with:
# 16 - LCD_BLR - RGB Red Cathode
# 17 - LCD_BLG - RGB Green Cathode (-)
# 18 - LCD_BLB - RGB Blue Cathode (-)




class PCF_CharLCD(ALCD.Adafruit_CharLCD):

    def __init__(self, pinmap=0, gpio=None, **kwargs):
        """
        Expects 'pinmap' as an index to select a pre-defined pin map or a
        dictionary defining a pin map similar to one of the pre-defined.

        Can specify gpio as a PCF8574 (or compatible GPIO) instance, or leave
        it out to get the default instance, or else specify address, busnum
        and/or i2c as needed to create a custom instance.
        """
        # get I2C GPIO expander instance
        if gpio is None:
                ioxargs = {}
                for kw in ('address', 'busnum', 'i2c'):
                        try:
                                ioxargs[kw] = kwargs[kw]
                                del kwargs[kw]
                        except KeyError:
                                pass
                iox = IOX.PCF8574(**ioxargs)
        else:
                iox = gpio
        self._storepinmap(pinmap)
        # Set LCD R/W pin to low - only writing to lcd
        iox.setup(PCF_RW, IOX.OUT)
        iox.output(PCF_RW, IOX.LOW)
        # Initialize LCD
        super(PCF_CharLCD, self).__init__(
            PCF_RS, PCF_EN,
            PCF_D4, PCF_D5, PCF_D6, PCF_D7,
            backlight=PCF_BL, invert_polarity=False,
            gpio=iox, **kwargs)


    # _storepinmap updates global pin mapping using the specified pinmap
    # at one time I thought this was needed to interop with other Adafruit
    # layers, but likely the only reason is to use global names in the
    # __init__ constructor above
    def _storepinmap(self, pinmap):
        # accept either a pinmap index or a pinmap dictionary
        try:
            m = PINMAPS[int(pinmap)]
        except TypeError:
            m = pinmap
        # use PINMAPS[0] as canonical list of keys we should update
        validkeys = PINMAPS[0].keys()
        # only update the keys we know
        globals().update(dict((k,v) for k,v in m.iteritems() if k in validkeys))
