#!/usr/bin/python

import json
import os
import time

from flask import Flask, Response
from logging.config import dictConfig
from paho.mqtt import client as mqtt

app = Flask(__name__)
metric_lifetime = int(os.getenv('DHT_METRIC_LIFETIME', '600'))

dictConfig({
    'version': 1,
    'root': {
        'level': os.environ.get('DHT_LOGLEVEL', 'INFO'),
    }
})


class Receiver(mqtt.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latest = {}

    def on_connect(self, client, userdata, flags, rc):
        app.logger.debug('subscribing to topics')
        self.subscribe('sensor/dht/#')

    def on_message(self, client, userdata, msg):
        app.logger.debug('received %s message: %s', msg.topic, msg.payload)
        data = json.loads(msg.payload)
        data['ts'] = time.time()
        self.latest[data['sensorid']] = data


@app.route('/metrics')
def publish_metrics():
    buf = []
    now = time.time()

    for sensor, data in app.metrics.latest.items():
        if now - data['ts'] > metric_lifetime:
            continue

        buf.append(f'temperature{{location="{data["location"]}", sensorid="{data["sensorid"]}"}} {data["t"]}')
        buf.append(f'humidity{{location="{data["location"]}", sensorid="{data["sensorid"]}"}} {data["h"]}')

    buf.append('')

    return Response('\n'.join(buf), mimetype='text/plain')


metrics = Receiver()
app.metrics = metrics
metrics.loop_start()
metrics.connect(os.environ['DHT_MQTT_SERVER'])
