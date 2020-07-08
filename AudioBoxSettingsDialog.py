#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AudioBoxSettingsDialog.py
MIT License (c) Faure Systems <dev at faure dot systems>

Dialog to configure plugin parameters.
"""

import os
import codecs
import configparser

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QGroupBox
from PyQt5.QtGui import QIcon


class AudioBoxSettingsDialog(QDialog):

    # __________________________________________________________________
    def __init__(self, settings, logger):

        super(AudioBoxSettingsDialog, self).__init__()

        self._logger = logger
        self._settings = settings
        self._currentOutput = None

        if 'output' in self._settings['parameters']:
            self._currentOutput = self._settings['parameters']['output']

        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(self.tr("Settings"))
        self.setWindowIcon(QIcon('./images/settings.svg'))
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        param_box = QGroupBox(self.tr("Audio output"))
        param_box_layout = QVBoxLayout(param_box)
        main_layout.addWidget(param_box)

        self._audioOutputSelector = QComboBox()
        self._audioOutputSelector.currentTextChanged.connect(self.onAudioOutputSelection)
        param_box_layout.addWidget(self._audioOutputSelector)

        info_default = QAudioDeviceInfo.defaultOutputDevice()
        self._audioOutputSelector.addItem(info_default.deviceName())

        output_devices = []
        for info in QAudioDeviceInfo.availableDevices(QAudio.AudioOutput):
            if info.deviceName() not in output_devices:
                self._audioOutputSelector.addItem(info.deviceName())
            output_devices.append(info.deviceName())

        if self._currentOutput is not None:
            current = self._audioOutputSelector.findText(self._currentOutput)
            if current >= 0:
                self._audioOutputSelector.setCurrentIndex(current)

        close_button = QPushButton(self.tr("Close"))
        close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        close_button.pressed.connect(self.accept)

    # __________________________________________________________________
    @pyqtSlot(str)
    def onAudioOutputSelection(self, s):

        self._logger.info(self.tr("Settings : set output device to {}".format(s)))
        self._settings['parameters']['output'] = s
