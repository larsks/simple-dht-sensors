# Simple temperature logger

Temperature and humidity logging via MQTT, published as prometheus metrics.

## ESP8266 sensor

The [MicroPython][] code in the [sensor/](sensor/) directory reads
temperature and humidity from a DHT22 sensor and published it to an
[MQTT][] message bus.

[micropython]: https://micropython.org
[mqtt]: https://en.wikipedia.org/wiki/MQTT

## Prometheus metrics

The Python code in the [server/](server/) directory reads sensor data
from an MQTT message bus and publishes it as [Prometheus][] metrics
that look like this:

[prometheus]: https://prometheus.io/

```
temperature{location="office", sensorid="2c3ae835a0d8"} 22.8
humidity{location="office", sensorid="2c3ae835a0d8"} 48.8
```
