from picoutil import read_page, read_lines
import network
import socket
from time import sleep
from machine import Pin
import rp2
import sys

def get_wlan_from_file(file):
    try:
        wlan = read_lines(file)
        print("ssid: '" + wlan[0] + "'")
        return wlan
    except:
        print("Provide wlan credentials.")
        sys.exit()

def load_index(file):
    try:
        html = read_page(file)
        return html
    except:
        print("Provide an index.html file.")
        sys.exit()

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

def serve(connection, http_handler):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        html = http_handler(request)
        client.send(html)
        client.close()

def wlan(wlan_file, http_handler):
    wlan = get_wlan_from_file(wlan_file)
    ip = connect(wlan[0], wlan[1])
    connection = open_socket(ip)
    serve(connection, http_handler)