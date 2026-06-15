import network
import urequests
import time
import display
import config

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

def main():
    oled = display.init()
    display.show(oled, ["Connecting...", "", "", ""])
    connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)
    while True:
        try:
            screens = fetch_data(config.HUB_URL)
            display.show(oled, screens[0]["lines"])
        except Exception as e:
            display.show(oled, ["Error fetching data", str(e), "", ""])
        time.sleep(config.POLL_INTERVAL)

main()