import network
import urequests
import time
from machine import Pin
import display
import config

TACT_PIN = 13
SLIDE_PIN = 14
LAYER_SIZE = 5
DEBOUNCE_MS = 200

screens = []
current_index = 0
_tact_flag = False
_last_tact_ms = 0

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass

def fetch_data(url):
    res = urequests.get(url)
    data = res.json()
    res.close()
    return data

def _on_tact(pin):
    global _tact_flag, _last_tact_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, _last_tact_ms) < DEBOUNCE_MS:
        return
    _last_tact_ms = now
    _tact_flag = True

def main():
    global screens, current_index, _tact_flag

    tact = Pin(TACT_PIN, Pin.IN, Pin.PULL_UP)
    slide = Pin(SLIDE_PIN, Pin.IN, Pin.PULL_UP)
    tact.irq(trigger=Pin.IRQ_FALLING, handler=_on_tact)

    oled = display.init()
    display.show(oled, ["Connecting...", "", "", ""])
    connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)

    try:
        screens = fetch_data(config.HUB_URL)
        if screens:
            display.show(oled, screens[0]["lines"])
    except Exception as e:
        display.show(oled, ["Error", str(e)[:20], "", ""])

    prev_layer = -1
    last_fetch_ms = time.ticks_ms()
    poll_ms = int(config.POLL_INTERVAL * 1000)

    while True:
        now = time.ticks_ms()
        layer = 1 if slide.value() == 0 else 0
        start = layer * LAYER_SIZE
        changed = False

        if layer != prev_layer:
            prev_layer = layer
            count = max(0, min(len(screens) - start, LAYER_SIZE))
            current_index = start if count > 0 else 0
            changed = True

        if _tact_flag:
            _tact_flag = False
            count = max(0, min(len(screens) - start, LAYER_SIZE))
            if count > 0:
                rel = (current_index - start + 1) % count
                current_index = start + rel
                changed = True

        if time.ticks_diff(now, last_fetch_ms) >= poll_ms:
            last_fetch_ms = now
            try:
                screens = fetch_data(config.HUB_URL)
                changed = True
            except Exception as e:
                display.show(oled, ["Error", str(e)[:20], "", ""])
                changed = False

        if changed and screens:
            idx = min(current_index, len(screens) - 1)
            display.show(oled, screens[idx]["lines"])

        time.sleep_ms(50)

main()
