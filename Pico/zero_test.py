from picozero import pico_led
from time import sleep

while True:
    pico_led.on()
    sleep(0.1)
    pico_led.off()
    sleep(0.1)