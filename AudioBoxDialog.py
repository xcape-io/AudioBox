#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AppletDialog.py
MIT License (c) Faure Systems <dev at faure dot systems>

Dialog to control PluginProps app running on Raspberry.
"""

import os
import codecs
import configparser

from constants import *
from AudioBoxSettingsDialog import AudioBoxSettingsDialog
from AudioOutputNotFoundDialog import AudioOutputNotFoundDialog
from AppletDialog import AppletDialog
from LedWidget import LedWidget

from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudioOutput, QAudio, QAudioFormat
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QPoint, QBuffer, QIODevice, QByteArray, QFile, QIODevice
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QComboBox


class AudioBoxDialog(AppletDialog):
    aboutToClose = pyqtSignal()
    publishMessage = pyqtSignal(str, str)
    switchLed = pyqtSignal(str, str)

    # __________________________________________________________________
    def __init__(self, title, icon, inbox, logger):

        self._inbox = inbox
        self._effects = {}
        self._effectButtons = {}
        self._sources = {}

        super().__init__(title, icon, logger)

        if 'output' in self._settings['parameters']:
            current_output = self._settings['parameters']['output']
            found = False
            for info in QAudioDeviceInfo.availableDevices(QAudio.AudioOutput):
                if info.deviceName() == current_output:
                    found = True
                    break
            if not found:
                self.warnignDialog()

        self.loadEffects()

        try:
            if UNSTOPPABLE:
                self.setWindowFlag(Qt.Tool)
        except:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        try:
            if ALWAYS_ON_TOP:
                self.setAttribute(Qt.WA_AlwaysStackOnTop)
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        except:
            pass

    # __________________________________________________________________
    def _buildUi(self):

        self._settings = configparser.ConfigParser()
        ini = 'settings.ini'
        if os.path.isfile(ini):
            self._settings.read_file(codecs.open(ini, 'r', 'utf8'))

        if 'parameters' not in self._settings.sections():
            self._settings.add_section('parameters')

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        self._led = LedWidget(BROKET_NAME, QSize(40, 20))
        self._led.setRedAsBold(True)
        self._led.setRedAsRed(True)
        self._led.switchOn('gray')

        settings_button = QPushButton()
        settings_button.setIcon(QIcon("./images/settings.svg"))
        settings_button.setFlat(True)
        settings_button.setToolTip(self.tr("Configuration"))
        settings_button.setIconSize(QSize(16, 16))
        settings_button.setFixedSize(QSize(24, 24))

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._led)
        header_layout.addWidget(settings_button, Qt.AlignRight)
        main_layout.addLayout(header_layout)

        for command, (title, _) in AUDIO_EFFECTS.items():
            button = QPushButton(title)
            self._effectButtons[button] = command
            button.pressed.connect(self.onEffectButton)
            main_layout.addWidget(button)

        main_layout.addStretch(0)

        self.setLayout(main_layout)

        settings_button.pressed.connect(self.onSettingsButton)
        self.switchLed.connect(self._led.switchOn)

    # __________________________________________________________________
    def closeEvent(self, e):

        try:
            if UNSTOPPABLE:
                e.ignore()
        except:
            self.aboutToClose.emit()

    # __________________________________________________________________
    @pyqtSlot()
    def onConnectedToMqttBroker(self):

        self._led.switchOn('green')

    # __________________________________________________________________
    def loadEffects(self):

        output_devices = {}
        for info in QAudioDeviceInfo.availableDevices(QAudio.AudioOutput):
            if info.deviceName() not in output_devices:
                output_devices[info.deviceName()] = info

        info = QAudioDeviceInfo.defaultOutputDevice()
        if 'output' in self._settings['parameters'] and self._settings['parameters']['output'] in output_devices:
            print(self._settings['parameters']['output'])
            info = output_devices[self._settings['parameters']['output']]
        else:
            self._settings['parameters']['output'] = info.deviceName()

        format = info.preferredFormat()

        self._effects.clear()
        for command, (_, file) in AUDIO_EFFECTS.items():
            output = QAudioOutput(info, format, self)
            output.stateChanged.connect(self.onOutputStateChanged)
            source = QFile(file)
            source.open(QIODevice.ReadOnly)
            source.seek(0)
            self._effects[command] = (output, source)
            self._sources[output] = source

    # __________________________________________________________________
    @pyqtSlot()
    def onDisconnectedToMqttBroker(self):

        self._led.switchOn('red')

    # __________________________________________________________________
    @pyqtSlot()
    def onEffectButton(self):

        button = self.sender()
        if button in self._effectButtons:
            print(self._settings['parameters']['output'])
            print(button.text(), self._effectButtons[button])
            command = self._effectButtons[button]
            try:
                output, source = self._effects[command]
                print(output.state())
                if output.state() == QAudio.ActiveState:
                    output.stop()
                    source.seek(0)
                output.start(source)
            except Exception as e:
                self._logger.error(self.tr("Kick audio effect failed, command not found: {}".format(command)))
                self._logger.debug(e)

    # __________________________________________________________________
    @pyqtSlot(str, str)
    def onMessageReceived(self, topic, message):

        if message.startswith("DISCONNECTED"):
            self._led.switchOn('yellow')
        else:
            if self._led.color() != 'green':
                self._led.switchOn('green')

        if topic == self._inbox and message.startswith("effect:"):
            _, _, command = message.partition(':')
            try:
                output, source = self._effects[command]
                print(output.state())
                if output.state() == QAudio.ActiveState:
                    output.stop()
                    source.seek(0)
                output.start(source)
            except Exception as e:
                self._logger.error(self.tr("Kick audio effect failed, command not found: {}".format(command)))
                self._logger.debug(e)

    # __________________________________________________________________
    @pyqtSlot(QAudio.State)
    def onOutputStateChanged(self, state):

        output = self.sender()

        if state == QAudio.ActiveState:
            print(output, 'Active')
        elif state == QAudio.SuspendedState:
            print(output, 'Suspended')
        elif state == QAudio.StoppedState:
            print(output, 'Stopped')
        elif state == QAudio.IdleState:
            print(output, 'Idle')
            if output in self._sources:
                self._sources[output].seek(0)
        elif state == QAudio.InterruptedState:
            print(output, 'Interrupted')
        else:
            print(output, 'Unexpected')

    # __________________________________________________________________
    @pyqtSlot()
    def onSettingsButton(self):

        dlg = AudioBoxSettingsDialog(self._settings, self._logger)
        dlg.setModal(True)
        dlg.move(self.pos() + QPoint(20, 20))
        dlg.exec()

        with open('settings.ini', 'w') as configfile:
            self._settings.write(configfile)

        self.loadEffects()

    # __________________________________________________________________
    def warnignDialog(self):
        dlg = AudioOutputNotFoundDialog(self._settings, self._logger)
        dlg.setModal(True)
        dlg.move(self.pos() + QPoint(20, 20))
        dlg.exec()

        with open('settings.ini', 'w') as configfile:
            self._settings.write(configfile)

        self.loadEffects()

