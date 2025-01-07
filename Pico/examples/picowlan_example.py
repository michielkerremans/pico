from picowlan import wlan, load_index
from picozero import pico_temp_sensor, pico_led
import sys

html = load_index("index.html")

pico_led.on()
state = 'ON'
temperature = 0

def http_handler(request):
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

wlan("wlan.txt", http_handler)