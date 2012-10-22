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
## \file AttributeDlg.py
# Attribute dialog class

import re
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import (QDialog, QDialogButtonBox)
from ui.ui_attributedlg import Ui_AttributeDlg


## dialog defining a tag attribute 
class AttributeDlg(QDialog, Ui_AttributeDlg):

    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(AttributeDlg, self).__init__(parent)
        
        ## attribute name
        self.name = u''
        ## attribute value
        self.value = u''
        self.setupUi(self)
        self._updateUi()

        self.connect(self.nameLineEdit, SIGNAL("textEdited(QString)"), self._updateUi)


    ## updates attribute user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        enable = not self.nameLineEdit.text().isEmpty()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)


    ## accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets and accept the dialog
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
        self.value = unicode(self.valueLineEdit.text())

        QDialog.accept(self)

if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## attribute form
    form = AttributeDlg()
    form.show()
    app.exec_() 

    if form.result():
        if form.name:
            print "Attribute: %s = \'%s\'" % ( form.name, form.value )
    
