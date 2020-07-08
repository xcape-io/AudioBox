#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
constants.py

Contains all the Room Control applet constants.
"""

# __________________________________________________________________
# Required by MqttApp
ORGANIZATIONDOMAIN = "xcape.io"
ORGANIZATIONNAME = "xcape.io"

CONFIG_FILE = '.config.yml'

APPLICATION = "AudioBox"

MQTT_DEFAULT_HOST = 'localhost'  # replace localhost with your broker IP address
MQTT_DEFAULT_PORT = 1883
MQTT_DEFAULT_QoS = 1

# __________________________________________________________________
# Required by AudioBox
APPDISPLAYNAME = "Audio Box"  # the Room Control application

# __________________________________________________________________
# Required by the widgets
LAYOUT_FILE = '.layout.yml'
LABELS_WIDTH = 30

# __________________________________________________________________
# Required by the application
BROKET_NAME = 'MQTT server connection'
ALWAYS_ON_TOP =  True
#UNSTOPPABLE =  True

AUDIO_EFFECTS = {}
AUDIO_EFFECTS['thunder1'] = ('Thunder Storm 1', 'audio/thunder1.wav')
AUDIO_EFFECTS['thunder2'] = ('Thunder Storm 2', 'audio/thunder2.wav')
AUDIO_EFFECTS['thunder3'] = ('Thunder Storm 3', 'audio/thunder3.wav')