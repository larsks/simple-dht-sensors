#!/bin/sh

exec mosquitto_sub -t 'sensor/#' >> $HOME/tmp/temp.log
