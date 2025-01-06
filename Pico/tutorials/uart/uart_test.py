from machine import Pin,UART
from time import sleep_ms

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart.init(bits=8, parity=None, stop=2)
led = Pin("LED", Pin.OUT)
led_state = 0
led.value(0)

uart.write("UART connected!\r\n")

while True:
    if uart.any():
        data = uart.read()
        if data== b't':
            led.toggle()
            led_state = 1 - led_state
            uart.write("LED toggled.\r\n")
            uart.write("LED state: " + str(led_state) + "\r\n")
    sleep_ms(100)