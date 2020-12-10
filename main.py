#!/usr/bin/python

import binascii
import dht
import ntptime
import json
import machine
import network
import time

import umqtt.robust as mqtt

from machine import RTC
from machine import Timer


rtc = RTC()
dhtpin = machine.Pin(4)
dhtsensor = dht.DHT22(dhtpin)
iface = network.WLAN(network.STA_IF)
sensorid = binascii.hexlify(iface.config('mac')).decode()
client = mqtt.MQTTClient(sensorid, '192.168.1.200')

t_init = Timer(-1)
t_sample = Timer(-1)

ledpin = machine.Pin(2, machine.Pin.OUT)
ledpin.on()


def loop(timer):
    global lastdata

    try:
        ledpin.off()

        try:
            for i in range(2):
                print('measuring (attempt=%s)' % i)
                try:
                    dhtsensor.measure()
                except OSError:
                    if i > 0:
                        raise

                    time.sleep(5)
                else:
                    break
        except OSError:
            print('ERROR: failed to measure temperature')
        else:
            lastdata = {
                'location': 'office',
                'sensorid': sensorid,
                'ts': time.localtime(),
                't': dhtsensor.temperature(),
                'h': dhtsensor.humidity(),
            }
            client.publish('sensor/office', json.dumps(lastdata))
    finally:
        ledpin.on()


def init(timer):
    print('setting time')
    ntptime.settime()

    print('connecting')
    client.connect()
    print('connected')

    loop(None)
    t_sample.init(period=30000, mode=Timer.PERIODIC, callback=loop)


def stop():
    t_sample.deinit()


t_init.init(period=5000, mode=Timer.ONE_SHOT, callback=init)
