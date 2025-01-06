import network
import socket
from time import sleep
from machine import Pin
import rp2
import sys

def connect(ssid, pwrd):
    picoled = Pin("LED", Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pwrd)
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        picoled.value(1)
        sleep(0.5)
        picoled.value(0)
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    picoled.value(1)
    return ip

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Van Eva!
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def serve(connection, handler):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        html = handler(request)
        client.send(html)
        client.close()

def pico_wlan(ssid, pwrd, handler):
    ip = connect(ssid, pwrd)
    connection = open_socket(ip)
    serve(connection, handler)