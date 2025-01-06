from picowlan import pico_wlan
from picoutil import read_page, read_lines
from picozero import pico_temp_sensor, pico_led
import sys

try:
    html = read_page("index.html")
    ssid = read_lines("login.txt")
    print("ssid: '" + ssid[0] + "'")
except:
    sys.exit()

pico_led.on()
state = 'ON'
temperature = 0

def handler(request):
    global state, temperature
    if request == '/lighton?':
        pico_led.on()
        state = 'ON'
    elif request =='/lightoff?':
        pico_led.off()
        state = 'OFF'
    elif request == '/close?':
        sys.exit()
    temperature = pico_temp_sensor.temp
    html2 = html.replace("{state}", state)
    html2 = html2.replace("{temperature}", str(temperature))
    return str(html2)

pico_wlan(ssid[0], ssid[1], handler)