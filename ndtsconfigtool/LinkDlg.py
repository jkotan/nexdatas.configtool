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
## \file LinkDlg.py
# Link dialog class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_linkdlg


## dialog defining a tag link 
class LinkDlg(QDialog, ui_linkdlg.Ui_LinkDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(LinkDlg, self).__init__(parent)
        
        ## link name
        self.name = u''
        ## link target
        self.target = u''
        self.setupUi(self)
        self.updateUi()

    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_nameLineEdit_textEdited(self, text):
        self.updateUi()

    ## updates link user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
        enable = not self.nameLineEdit.text().isEmpty()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    ## accepts input text strings
    # \brief It copies the link name and target from lineEdit widgets and accept the dialog
    def accept(self):
        class CharacterError(Exception): pass
        name = unicode(self.nameLineEdit.text())
        
        try:
            if 1 in [c in name for c in '!"#$%&\'()*+,/;<=>?@[\\]^`{|}~']:
                raise CharacterError, ("Name contains one of forbidden characters") 
            if name[0] == '-':
                raise CharacterError, ("The first character of Name is '-'") 

        except CharacterError, e:   
            QMessageBox.warning(self, "Character Error", unicode(e))
            return
        self.name = name
        self.target = unicode(self.targetLineEdit.text())

        QDialog.accept(self)

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## link form
    form = LinkDlg()
    form.show()
    app.exec_()

    if form.result():
        if form.name:
            print "Link: %s = \'%s\'" % ( form.name, form.target )
    
