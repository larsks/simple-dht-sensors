#!/usr/bin/python

import binascii
import dht
import json
import machine
import network
import time

import umqtt.robust as mqtt

from machine import RTC
from machine import Timer

import config


rtc = RTC()
dhtpin = machine.Pin(config.dht_pin)
dhtsensor = dht.DHT22(dhtpin)
iface = network.WLAN(network.STA_IF)

# use mac address for client id
sensorid = binascii.hexlify(iface.config('mac')).decode()
client = mqtt.MQTTClient(sensorid, config.mqtt_server)

t_init = Timer(-1)
t_sample = Timer(-1)

ledpin = machine.Pin(config.led_pin, machine.Pin.OUT)
ledpin.on()


def loop(timer):
    global lastdata
    global count

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
                'location': config.location,
                'sensorid': sensorid,
                't': dhtsensor.temperature(),
                'h': dhtsensor.humidity(),
            }
            client.publish(
                'sensor/dht/{}/{}'.format(config.location, sensorid),
                json.dumps(lastdata)
            )
    finally:
        ledpin.on()


def init():
    print('connecting')
    client.connect()
    print('connected')

    loop(None)
    t_sample.init(period=config.loop_interval,
                  mode=Timer.PERIODIC, callback=loop)


def stop():
    t_sample.deinit()


print('waiting for connection')
while not iface.isconnected():
    time.sleep(1)

init()
