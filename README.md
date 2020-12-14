# Simple temperature logger

Reads temperature and humidity from a DHT22 sensor, and publishes them to an
MQTT message bus. Uses virtual timers to run the sampling in the
"background" so you can still interact with the REPL.
