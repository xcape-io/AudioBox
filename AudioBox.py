#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AudioBox.py
MIT License (c) Faure Systems <dev at faure dot systems>

AudioBox application extends MqttApp.
"""

from constants import *
from MqttApplet import MqttApplet
from AudioBoxDialog import AudioBoxDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class AudioBox(MqttApplet):

    # __________________________________________________________________
    def __init__(self, argv, client, debugging_mqtt=False):
        super().__init__(argv, client, debugging_mqtt)

        self.setApplicationDisplayName(APPDISPLAYNAME)

        self._AppletDialog = AudioBoxDialog('', './wave.svg',
                                            self._definitions['mqtt-sub-effects'], self._logger)
        self._AppletDialog.aboutToClose.connect(self.exitOnClose)
        self._AppletDialog.publishMessage.connect(self.publishMessage)

        self.connectedToMqttBroker.connect(self._AppletDialog.onConnectedToMqttBroker)
        self.disconnectedToMqttBroker.connect(self._AppletDialog.onDisconnectedToMqttBroker)
        self.messageReceived.connect(self._AppletDialog.onMessageReceived)

        try:
            if HIDE_APPLET:
                pass
        except:
            self._AppletDialog.show()

    # __________________________________________________________________
    @pyqtSlot()
    def exitOnClose(self):
        self._logger.info(self.tr("exitOnClose "))
        self.quit()
