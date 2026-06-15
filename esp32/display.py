from machine import Pin, I2C
import ssd1306
from writer import Writer
import jpfont

_wri = None

def init():
    global _wri
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    _wri = Writer(oled, jpfont, verbose=False)
    return oled

def show(oled, lines):
    oled.fill(0)
    for i, line in enumerate(lines):
        Writer.set_textpos(oled, i * 16, 0)
        _wri.printstring(line)
    oled.show()
