from machine import Pin, I2C
import ssd1306
from bfont import BinaryFont

_font = None

def init():
    global _font
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    _font = BinaryFont('jpfont.bin')
    return oled

def show(oled, lines):
    oled.fill(0)
    for i, line in enumerate(lines):
        _font.draw_string(oled, 0, i * 16, line)
    oled.show()
