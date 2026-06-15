from machine import Pin, I2C
import ssd1306

def init():
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    return oled

def show(oled, lines):
    oled.fill(0)
    oled.text(lines[0], 0, 0)
    oled.text(lines[1], 0, 16)
    oled.text(lines[2], 0, 32)
    oled.text(lines[3], 0, 48)
    oled.show()
