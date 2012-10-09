#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_connectdlg


## dialog defining a tag connect 
class ConnectDlg(QDialog, ui_connectdlg.Ui_ConnectDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(ConnectDlg, self).__init__(parent)
        
        ## device name
        self.device = u''
        ## host name
        self.host = u''
        ## port
        self.port = None
        self.setupUi(self)
        self.updateUi()


        self.connect(self.connectPushButton, SIGNAL("clicked()"), self.accept)
        self.connect(self.cancelPushButton, SIGNAL("clicked()"), self.reject)


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_deviceLineEdit_textEdited(self, text):
        self.updateUi()

    ## updates connect user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
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
            port = unicode(self.portLineEdit.text())
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

        
        QDialog.accept(self)

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## connect form
    form = ConnectDlg()
    form.show()
    app.exec_() 

    if form.result():
        if form.device:
            print "Connect: %s , %s , %s" % ( form.device, form.host, form.port )
    
