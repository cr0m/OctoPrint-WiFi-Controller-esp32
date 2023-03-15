import time
import json
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
from secrets import secrets

printer_ip = secrets["printer_ip"]
TOOL_JSON_URL = "http://%s/api/printer/tool" % printer_ip
BED_JSON_URL = "http://%s/api/printer/bed" % printer_ip
GEN_JSON_URL = "http://%s/api/printer?apikey=%s" % (printer_ip, secrets["octo_api_key"])

headers = {
    "X-Api-Key": secrets["octo_api_key"],
    "Content-Type": "application/json",
}

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())


def connetWiFi():
    print("Connecting to ",secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected to %s!" % secrets["ssid"])
    print("DHCP IP:", wifi.radio.ipv4_address)
    print("Latency check to printer: %f ms" % (wifi.radio.ping(ipaddress.ip_address(secrets["printer_ip"])) * 1000))
connetWiFi()


def setBed(temp):
    print("Setting Bed Temp to :", temp)
    try:
        bed_json_to_send = {"command": "target", "target": temp}
        bj2s = json.dumps(bed_json_to_send)
        r8 = requests.post(BED_JSON_URL, data=bj2s, headers=headers)
        print("")
    except Exception as e:
        print("Error Setting Bed Temp: ", e)


def setHotend(temp):
    print("Setting Hotend Temp to :", temp)
    try:
        tool_json_to_send = {"command": "target", "targets": {"tool0": temp}}
        tj2s = json.dumps(tool_json_to_send)
        r9 = requests.post(TOOL_JSON_URL, data=tj2s, headers=headers)
        print("")
    except Exception as e:
        print("Error Setting Hotend Temp: ", e)


def getStatus():
    try:
        #print("getting request from ", GEN_JSON_URL)
        r1 = requests.get(GEN_JSON_URL)
        time.sleep(0.5)
        json_data = r1.json()
        time.sleep(2)
        r1.close()
        actual_he_temp = json_data["temperature"]["tool0"]["actual"]
        target_he_temp = json_data["temperature"]["tool0"]["target"]
        actual_bed_temp = json_data["temperature"]["bed"]["actual"]
        target_bed_temp = json_data["temperature"]["bed"]["target"]
        print("Hot end : current: %s // target: %s" % (actual_he_temp, target_he_temp))
        print("    Bed : current: %s // target: %s" % (actual_bed_temp, target_bed_temp))
        time.sleep(2)
    except Exception as e:
        print("Error getting printer status: ", e)
        time.sleep(15)

print("\n" * 4)

getStatus()
print()
setBed(0)
setHotend(0)

getStatus()
print("\n" * 4)