import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import rp2
import sys

ssid = ""
pwrd = ""

def login():
    global ssid, pwrd
    try:
        page = open("login.txt",'r')
        lines = page.read().split('\r\n')
        page.close()
        ssid = lines[0]
        pwrd = lines[1]
    except:
        print("File not found.")
        sys.exit()

def connect(ssid, pwrd):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pwrd)
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    return ip

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def webpage(temperature, state):
    #Template HTML
    page = open("index.html","r")
    html = page.read()
    page.close()
    html = html.replace("{state}", state)
    html = html.replace("{temperature}", str(temperature))
    return str(html)

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

state = 'ON'
pico_led.on()
temperature = 0

def myhandler(request):
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
    return webpage(temperature, state)

login()
print("ssid: '" + ssid + "'")
ip = connect(ssid, pwrd)
connection = open_socket(ip)
serve(connection, myhandler)