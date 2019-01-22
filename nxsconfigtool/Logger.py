#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
# \package nxsconfigtool nexdatas
# \file Loggers.py
# Logger classes

""" "Component Desigener Loggers  """

import logging
import sys

from PyQt5.QtCore import (QObject, pyqtSignal)

logger = logging.getLogger("nxsdesigner")

if sys.version_info > (3,):
    unicode = str


class LogHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        message = self.format(record)
        if message:
            LogStream.stdout().write("%s\n" % message)


class LogActions(QObject):
    levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    def __init__(self, receiver):
        self.receiver = receiver

    def updatelevel(self):
        levellist = ['no', 'debug', 'info', 'warning', 'error', 'critical']
        eflevel = logger.getEffectiveLevel()
        ilv = eflevel // 10
        level = levellist[ilv]
        self.setlevel(level, True)

    def setlevel(self, level, flag):
        level = level if flag else None
        logger.setLevel(
            self.levels.get(level, logging.NOTSET))
        for lv in self.levels:
            name = "action" + lv[0].upper() + lv[1:]
            if lv != level or not flag:
                if hasattr(self.receiver.ui, name):
                    action = getattr(self.receiver.ui, name)
                    action.setChecked(False)
            else:
                if hasattr(self.receiver.ui, name):
                    action = getattr(self.receiver.ui, name)
                    action.setChecked(True)
        if level in self.levels and flag:
            logger.info("set log level: %s" % level)


class LogStream(QObject):

    written = pyqtSignal(str)
    _stdout = None

    @staticmethod
    def stdout():
        if not LogStream._stdout:
            LogStream._stdout = LogStream()
        return LogStream._stdout

    def write(self, message):
        if not self.signalsBlocked():
            self.written.emit(unicode(message))

    def flush(self):
        pass

    def fileno(self):
        return -1
