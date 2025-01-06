# Adapted from https://RandomNerdTutorials.com/micropython-esp32-bluetooth-low-energy-ble/
from machine import Pin
from micropython import const
import asyncio
import aioble
import bluetooth
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

def _led_off():
    global led_state
    led_state = 0
    led.value(led_state)
    led_ext.value(led_state)
    print("LED OFF:", led_state)

def _led_toggle():
    global led_state
    led_state = 1 - led_state
    led.value(led_state)
    led_ext.value(led_state)
    print("LED TOGGLED:", led_state)

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

# BLUETOOTH FUNCTIONS

# https://www.uuidgenerator.net/
_BLE_SERVICE_UUID = bluetooth.UUID('5889b854-37a2-4b78-8a07-4401d4973d39')
_BLE_READ_UUID = bluetooth.UUID('96aaa682-21d6-4498-af04-baa13eb8a01c')
_BLE_WRITE_UUID = bluetooth.UUID('d76c8db4-db2b-44ee-8ba6-088a1f8ba7e4')
_ADV_INTERVAL_MS = 250_000

ble_service = aioble.Service(_BLE_SERVICE_UUID)
ble_read = aioble.Characteristic(ble_service, _BLE_READ_UUID, read=True, notify=True)
ble_write = aioble.Characteristic(ble_service, _BLE_WRITE_UUID, read=True, write=True, notify=True, capture=True)

aioble.register_services(ble_service)

def _encode_data(data):
    return str(data).encode('utf-8')

def _decode_data(data):
    try:
        if data is not None:
            return data.decode('utf-8')
    except Exception as e:
        print("Error decoding:", e)
        return None

async def read_task():
    while True:
        if _is_pressed_and_debounced():
            ble_read.write(_encode_data("Button pressed.\r\n"), send_update=True)
        await asyncio.sleep_ms(100)

async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="mpy_ble",
                services=[_BLE_SERVICE_UUID],
                ) as connection:
                    print("Connection from", connection.device)
                    await connection.disconnected()
        except asyncio.CancelledError:
            print("Peripheral task cancelled.")
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            await asyncio.sleep_ms(100)

async def wait_for_write():
    while True:
        try:
            connection, data = await ble_write.written()
            data = _decode_data(data).strip("\r\n")
            print('Data: ', data)
            global led_state
            if data == "on":
                _led_on()
            elif data == "off":
                _led_off()
            elif data == "toggle":
                _led_toggle()
            else:
                print("Unknown command.")
        except asyncio.CancelledError:
            print("Write task cancelled.")
        except Exception as e:
            print("Error in write_task:", e)
        finally:
            await asyncio.sleep_ms(100)


async def main():
    t1 = asyncio.create_task(read_task())
    t2 = asyncio.create_task(peripheral_task())
    t3 = asyncio.create_task(wait_for_write())
    await asyncio.gather(t1, t2)

asyncio.run(main())