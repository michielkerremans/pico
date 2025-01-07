# Adapted from https://RandomNerdTutorials.com/micropython-esp32-bluetooth-low-energy-ble/
from machine import Pin
from picoble import ble_init, ble_write, ble_print, ble_serve
import struct
import time

led = Pin("LED", Pin.OUT)
led_ext = Pin(15, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

_DEBOUNCE_INTERVAL_MS = 300

led.value(0)
led_ext.value(0)

# LED FUNCTIONS

led_state = 0

def _led_on():
    global led_state
    led_state = 1
    led.value(led_state)
    led_ext.value(led_state)
    print("LED ON:", led_state)
    ble_print("LED ON: " + str(led_state))

def _led_off():
    global led_state
    led_state = 0
    led.value(led_state)
    led_ext.value(led_state)
    print("LED OFF:", led_state)
    ble_print("LED OFF: " + str(led_state))

def _led_toggle():
    global led_state
    led_state = 1 - led_state
    led.value(led_state)
    led_ext.value(led_state)
    print("LED TOGGLED:", led_state)
    ble_print("LED TOGGLED: " + str(led_state))

# BUTTON FUNCTIONS

debounce_time = 0

def _is_debounced():
    global debounce_time
    if ((time.ticks_ms() - debounce_time) > _DEBOUNCE_INTERVAL_MS):
        debounce_time = time.ticks_ms()
        return True
    else:
        return False

def _is_pressed():
    return button.value() is 1

def _is_pressed_and_debounced():
    return _is_pressed() and _is_debounced()

def ble_write_handler():
    if _is_pressed_and_debounced():
        ble_write("Button pressed.\r\n")

def ble_read_handler(data):
    data = data.strip("\r\n")
    print("Data: ", data)
    global led_state
    if data == "on":
        _led_on()
    elif data == "off":
        _led_off()
    elif data == "toggle":
        _led_toggle()
    else:
        print("Unknown command.")
    return

ble_init("ble_uuid.txt")
ble_serve(ble_write_handler, ble_read_handler, 250_000)