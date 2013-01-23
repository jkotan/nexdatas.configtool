#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndtsconfigtool nexdatas
## \file ConnectDlg.py
# Connect dialog class

import re
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import (QDialog, QMessageBox)
from ui.ui_connectdlg import Ui_ConnectDlg


## dialog defining a tag connect 
class ConnectDlg(QDialog, Ui_ConnectDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(ConnectDlg, self).__init__(parent)
        
        ## device name of the configuration server
        self.device = u''
        ## host name of the configuration server
        self.host = u''
        ## port of the configuration server
        self.port = None

    ## creates GUI    
    # \brief It updates GUI and creates connection for required actions
    def createGUI(self):
        self.setupUi(self)
        self.updateForm()
        self._updateUi()


        self.connect(self.connectPushButton, SIGNAL("clicked()"), self.accept)
        self.connect(self.cancelPushButton, SIGNAL("clicked()"), self.reject)
        self.connect(self.deviceLineEdit, SIGNAL("textEdited(QString)"), self._updateUi)

        

    ## updates the connect dialog
    # \brief It sets initial values of the connection form
    def updateForm(self):
        if self.device is not None:
            self.deviceLineEdit.setText(self.device)
        if self.host is not None:
            self.hostLineEdit.setText(self.host)
        if self.port is not None:
            self.portLineEdit.setText(str(self.port))


    ## updates connect user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        enable = not self.deviceLineEdit.text().isEmpty()
        self.connectPushButton.setEnabled(enable)


    ## accepts input text strings
    # \brief It copies the connect name and value from lineEdit widgets and accept the dialog
    def accept(self):
        class CharacterError(Exception): pass
        device = unicode(self.deviceLineEdit.text())
        if not device: 
            QMessageBox.warning(self, "Empty device name", 
                                "Please define the device name")
            self.deviceLineEdit.setFocus()
            return
        
        self.device = device
        self.host = unicode(self.hostLineEdit.text())
        
        self.port = None
        try:
            port = str(self.portLineEdit.text())
            if port:
                self.port = int(port)
        except:
            QMessageBox.warning(self, "Wrong port number", 
                                "Please define the port number")
            self.portLineEdit.setFocus()
            return
            
        if self.port is not None and  not self.host:
            QMessageBox.warning(self, "Empty host name", 
                                "Please define the host name")
            self.hostLineEdit.setFocus()
            return

        if self.port is None and self.host:
            QMessageBox.warning(self, "Empty port", 
                                "Please define the port")
            self.portLineEdit.setFocus()
            return

        QDialog.accept(self)

if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

   ## Qt application
    app = QApplication(sys.argv)
    ## connect form
    form = ConnectDlg()
    form.createGUI()
    form.show()
    app.exec_() 

    if form.result():
        if form.device:
            print "Connect: %s , %s , %s" % ( form.device, form.host, form.port )
    
