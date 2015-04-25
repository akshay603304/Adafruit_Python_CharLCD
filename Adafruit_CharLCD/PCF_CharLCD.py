

import Adafruit_GPIO.PCF8574 as IOX
import Adafruit_CharLCD as ALCD


# Char LCD pin to I/O extender GPIO pin number maps
PINMAPS = [
{ # map 0 - generic black PCB
'PCF_RS': 0,
'PCF_RW': 1,
'PCF_EN': 2,
'PCF_BL': 3,
'PCF_D4': 4,
'PCF_D5': 5,
'PCF_D6': 6,
'PCF_D7': 7,
}, { # map 1
'PCF_RS': 0,
'PCF_RW': 1,
'PCF_EN': 2,
'PCF_BL': 3,
'PCF_D4': 6,
'PCF_D5': 5,
'PCF_D6': 4,
'PCF_D7': 7,
}, { # map 2
'PCF_RS': 4,
'PCF_RW': 5,
'PCF_EN': 6,
'PCF_BL': 7,
'PCF_D4': 0,
'PCF_D5': 1,
'PCF_D6': 2,
'PCF_D7': 3,
},
]




class PCF_CharLCD(ALCD.Adafruit_CharLCD):

    def __init__(self, pinmap=0, **kwargs):
        # get I2C GPIO expander instance
        ioxargs = dict((k,v) for k,v in kwargs.iteritems() if k in ('address','busnum','i2c'))
        iox = kwargs.get('gpio') or IOX.PCF8574(**ioxargs)
        # remove iox args from kwargs
        for k in ('address','busnum','i2c','gpio'):
            try:
                del kwargs[k]
            except KeyError:
                pass
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


    def _storepinmap(self, pinmap):
        try:
            m = PINMAPS[int(pinmap)]
        except TypeError:
            m = pinmap
        validkeys = PINMAPS[0].keys()
        globals().update(dict((k,v) for k,v in m.iteritems() if k in validkeys))
