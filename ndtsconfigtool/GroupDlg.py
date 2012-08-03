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
## \file GroupDlg.py
# Group dialog class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_groupdlg


## dialog defining a tag group
class GroupDlg(QDialog, ui_groupdlg.Ui_GroupDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(GroupDlg, self).__init__(parent)
        
        ## group name
        self.name = u''
        ## group type
        self.nexusType = u''
        ## group doc
        self.doc = u''
        ## group attributes
        self.attributes = {}
#        self.attributes = {"sdfdfsf":"sdffd","sdas":"23423"}

        self.setupUi(self)
        self.updateUi()

        self.populateAttributes()




    ## fills in the attribute table      
    # \param selectedAttribute selected attribute    
    def populateAttributes(self, selectedAttribute = None):
        selected = None
        self.attributeTableWidget.clear()
        self.attributeTableWidget.setSortingEnabled(False)
        self.attributeTableWidget.setRowCount(len(self.attributes))
        headers = ["Name", "Value"]
        self.attributeTableWidget.setColumnCount(len(headers))
        self.attributeTableWidget.setHorizontalHeaderLabels(headers)	
        self.attributeTableWidget.horizontalHeader().setStretchLastSection(True);
        for row, name in enumerate(self.attributes):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            if selectedAttribute is not None and selectedAttribute == name:
                selected = item
            self.attributeTableWidget.setItem(row, 0, item)
            self.attributeTableWidget.setItem(row, 1, QTableWidgetItem(self.attributes[name]))
        self.attributeTableWidget.setSortingEnabled(True)
        self.attributeTableWidget.resizeColumnsToContents()
        if selected is not None:
            selected.setSelected(True)
            self.attributeTableWidget.setCurrentItem(selected)
            
                
                
            



    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_typeLineEdit_textEdited(self, text):
        self.updateUi()

    ## updates group user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
        enable = not self.typeLineEdit.text().isEmpty()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    ## accepts input text strings
    # \brief It copies the group name and type from lineEdit widgets and accept the dialog
    def accept(self):
        self.name = unicode(self.nameLineEdit.text())
        self.nexusType = unicode(self.typeLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())
        
        QDialog.accept(self)

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = GroupDlg()
    form.show()
    app.exec_()
    if form.nexusType:
        print "Group: name = \'%s\' type = \'%s\'" % ( form.name, form.nexusType )
    if form.doc:
        print "Doc: \n%s" % form.doc
    
