#!/usr/bin/python

import binascii
import dht
import json
import machine
import network
import time

import umqtt.robust as mqtt

from machine import Timer

import config

dhtpin = machine.Pin(4)
dhtsensor = dht.DHT22(dhtpin)
iface = network.WLAN(network.STA_IF)

# use mac address for client id
sensorid = binascii.hexlify(iface.config('mac')).decode()
client = mqtt.MQTTClient(sensorid, config.mqtt_server)

ledpin = machine.Pin(2, machine.Pin.OUT)
ledpin.on()


def deepsleep(duration):
    assert duration > 0

    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, duration)
    print('sleeping for {} ms'.format(duration))
    machine.deepsleep()


def measure():
    global lastdata

    try:
        if config.blink_led:
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
            print('! failed to measure temperature')
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


def wait_for_connection():
    print('waiting for wifi')
    while not iface.isconnected():
        machine.idle()
    print('wifi connected')


def run():
    t_start = time.ticks_ms()

    wait_for_connection()

    print('connecting to mqtt server')
    client.connect()
    print('connected')

    measure()
    print('wait 5 seconds before sleeping')
    time.sleep(5)

    t_end = time.ticks_ms()
    t_delta = time.ticks_diff(t_end, t_start)
    print('start', t_start, 'end', t_end, 'delta', t_delta)
    deepsleep(config.measure_interval - time.ticks_diff(t_end, t_start))


run()
