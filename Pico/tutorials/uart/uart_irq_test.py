from machine import Pin,UART
from time import sleep_ms

uart = UART(0, baudrate = 9600, tx = Pin(0), rx = Pin(1))
uart.init(bits = 8, parity = None, stop = 2)
led = Pin("LED", Pin.OUT)
led_state = 0
led.value(0)

uart.write("UART connected!\r\n\r\n")

buffer = ""

# Van Eva!
def uart_callback(data):
    global buffer, led_state
    data = uart.read()
    if data == b'\r':
        uart.write("\r\n")
        if buffer == "toggle":
            led.toggle()
            led_state = 1 - led_state
            uart.write("LED toggled.\r\n")
            uart.write("LED state: " + str(led_state) + "\r\n")
        else:
            uart.write("... unknown command ...\r\n")
        uart.write("\r\n")
        buffer = ""
    elif data == b'\x7f': # backspace
        uart.write(data)
        buffer = buffer[:-1]
    else:
        uart.write(data)
        buffer += data.decode('utf-8')

uart.irq(handler = uart_callback, trigger = UART.IRQ_RXIDLE, hard = False)