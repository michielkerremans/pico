# Adapted from https://RandomNerdTutorials.com/micropython-esp32-bluetooth-low-energy-ble/
from picoutil import read_page, read_lines
import asyncio
import aioble
import bluetooth
import sys

def get_uuids_from_file(file):
    try:
        uuids = read_lines(file)
        print("BLE_SERVICE_UUID: '" + uuids[0] + "'")
        print("BLE_READ_UUID: '" + uuids[1] + "'")
        print("BLE_WRITE_UUID: '" + uuids[2] + "'")
        return uuids
    except:
        print("No UUIDs found, try https://www.uuidgenerator.net/ !")
        sys.exit()

_ble_service_uuid = ""
_ble_read_uuid = ""
_ble_write_uuid = ""
_ble_service = None
_ble_read_char = None
_ble_write_char = None

def ble_register(uuids):
    global _ble_service_uuid, _ble_read_uuid, _ble_write_uuid
    _ble_service_uuid = bluetooth.UUID(uuids[0])
    _ble_read_uuid = bluetooth.UUID(uuids[1])
    _ble_write_uuid = bluetooth.UUID(uuids[2])
    global _ble_service, _ble_read_char, _ble_write_char
    _ble_service = aioble.Service(_ble_service_uuid)
    _ble_read_char = aioble.Characteristic(_ble_service, _ble_read_uuid, read=True, notify=True)
    _ble_write_char = aioble.Characteristic(_ble_service, _ble_write_uuid, read=True, write=True, notify=True, capture=True)
    aioble.register_services(_ble_service)

def ble_write(data):
    global _ble_read_char
    _ble_read_char.write(str(data).encode('utf-8'), send_update=True)

ble_write_buffer = ""

def ble_print(data):
    global ble_write_buffer
    ble_write_buffer = str(data) + "\r\n"

async def _ble_advertise_task(adv_interval_ms):
    global _ble_service_uuid
    while True:
        try:
            async with await aioble.advertise(
                adv_interval_ms,
                name="mpy_ble",
                services=[_ble_service_uuid],
                ) as connection:
                    print("Connection from", connection.device)
                    await connection.disconnected()
        except asyncio.CancelledError:
            print("ble_advertise cancelled.")
        except Exception as e:
            print("Error in ble_advertise:", e)
        finally:
            await asyncio.sleep_ms(100)

async def _ble_write_task(ble_write_handler):
    global ble_write_buffer
    while True:
        if ble_write_buffer != "":
            ble_write(ble_write_buffer)
            ble_write_buffer = ""
        else:
            ble_write_handler()
        await asyncio.sleep_ms(100)

async def _ble_read_task(ble_read_handler):
    global _ble_write_char
    while True:
        try:
            connection, data = await _ble_write_char.written()
            if data is not None:
                data = data.decode('utf-8')
            ble_read_handler(data)
        except asyncio.CancelledError:
            print("ble_read cancelled.")
        except Exception as e:
            print("Error in ble_read:", e)
        finally:
            await asyncio.sleep_ms(100)

async def _ble_main(ble_write_handler, ble_read_handler, ble_adv_interval_ms):
    t1 = asyncio.create_task(_ble_write_task(ble_write_handler))
    t2 = asyncio.create_task(_ble_advertise_task(ble_adv_interval_ms))
    t3 = asyncio.create_task(_ble_read_task(ble_read_handler))
    await asyncio.gather(t1, t2)

def ble_init(file):
    ble_uuids = get_uuids_from_file(file)
    ble_register(ble_uuids)

def ble_serve(ble_write_handler, ble_read_handler, ble_adv_interval_ms):
    asyncio.run(_ble_main(ble_write_handler, ble_read_handler, ble_adv_interval_ms))