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
# \file ComponentDlg.py
# component classes

""" component widget """

from PyQt5.QtWidgets import (QDialog, QWidget)
from PyQt5 import uic

# from .ui.ui_componentdlg import Ui_ComponentDlg
from .DomTools import DomTools

import logging
import os
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "componentdlg.ui"))


# compoent dialog
class ComponentDlg(QDialog):

    # constructor
    # \param component component instance
    # \param parent patent instance
    def __init__(self, component, parent=None):
        super(ComponentDlg, self).__init__(parent)
        # component instance
        self.component = component

        # user interface
        self.ui = _formclass()

        # default widget
        self.ui.widget = QWidget(self)

    # provides row number of the given node
    # \param child child item
    # \returns row number
    def getWidgetNodeRow(self, child):
        if self.ui and self.ui.widget:
            return DomTools.getNodeRow(child, self.ui.widget.node)
        else:
            logger.warn("Widget does not exist")

    # sets focus on save button
    # \brief It sets focus on save button
    def setSaveFocus(self):
        if self.ui:
            self.ui.savePushButton.setFocus()

    # closes the window and cleans the dialog label
    # \param event closing event
    def closeEvent(self, event):
        super(ComponentDlg, self).closeEvent(event)
        self.component.dialog = None
        event.accept()

    # rejects component closing
    def reject(self):
        self.parent().close()
        super(ComponentDlg, self).reject()


if __name__ == "__main__":
    pass
