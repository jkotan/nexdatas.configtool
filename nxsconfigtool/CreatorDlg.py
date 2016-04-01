#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsconfigtool nexdatas
## \file CreatorDlg.py
# Component Creator dialog class

""" server creator widget """

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog

from .ui.ui_creatordlg import Ui_CreatorDlg

import logging
## message logger
logger = logging.getLogger("nxsdesigner")


## dialog defining a component creator dialog
class CreatorDlg(QDialog):

    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(CreatorDlg, self).__init__(parent)

        ## host name of the configuration server
        self.components = []
        self.componentName = None
        ## user interface
        self.ui = Ui_CreatorDlg()
        self.action = ''

    ## creates GUI
    # \brief It updates GUI and creates creatorion for required actions
    def createGUI(self):
        self.ui.setupUi(self)
        self.updateForm()

        self.connect(self.ui.savePushButton, SIGNAL("clicked()"),
                     self.savePressed)
        self.connect(self.ui.storePushButton, SIGNAL("clicked()"),
                     self.storePressed)
        self.connect(self.ui.applyPushButton, SIGNAL("clicked()"),
                     self.applyPressed)
        self.connect(self.ui.cancelPushButton, SIGNAL("clicked()"),
                     self.reject)

    ## updates the connect dialog
    # \brief It sets initial values of the connection form
    def updateForm(self):
        self.ui.compComboBox.clear()
        if self.components:
            self.ui.compComboBox.addItems(self.components)

    def savePressed(self):
        self.componentName = unicode(self.ui.compComboBox.currentText())
        self.action = 'SAVE'
        QDialog.accept(self)

    def storePressed(self):
        self.componentName = unicode(self.ui.compComboBox.currentText())
        self.action = 'STORE'
        QDialog.accept(self)

    def applyPressed(self):
        self.componentName = unicode(self.ui.compComboBox.currentText())
        self.action = 'APPLY'
        QDialog.accept(self)


if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    ## Qt application
    app = QApplication(sys.argv)
    ## connect form
    form = CreatorDlg()
    form.createGUI()
    form.show()
    app.exec_()

    if form.result():
        if form.device:
            logger.info("Connect: %s , %s , %s" %
                        (form.device, form.host, form.port))
