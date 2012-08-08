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
## \file FieldDlg.py
# Field dialog class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_fielddlg

from AttributeDlg import AttributeDlg
from DimensionsDlg import DimensionsDlg

## dialog defining a field tag
class FieldDlg(QDialog, ui_fielddlg.Ui_FieldDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(FieldDlg, self).__init__(parent)
        
        ## field name
        self.name = u''
        ## field type
        self.nexusType = u''
        ## field units
        self.units = u''
        ## field value
        self.value = u''
        ## field doc
        self.doc = u''
        ## dimensions doc
        self.dimDoc = u''
        ## field attributes
        self.attributes = {}

        ## rank
        self.rank = 0
        ## dimensions
        self.dimensions = []


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)

        if self.name :
            self.nameLineEdit.setText(self.name) 
        if self.nexusType :
            self.typeLineEdit.setText(self.nexusType) 
        if self.doc :
            self.docTextEdit.setText(self.doc)
        if self.units:    
            self.unitsLineEdit.setText(self.units)
        if self.value:    
            self.valueLineEdit.setText(self.value)

        if self.rank < len(self.dimensions) :
            self.rank = len(self.dimensions)
        
        if self.dimensions:
            label = self.dimensions.__str__()
            self.dimLabel.setText("Dimensions: %s" % label)



        self.updateUi()

        self.connect(self.attributeTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.tableItemChanged)
        self.connect(self.addPushButton, SIGNAL("clicked()"), 
                     self.addAttribute)
        self.connect(self.removePushButton, SIGNAL("clicked()"), 
                     self.removeAttribute)
        self.connect(self.dimPushButton, SIGNAL("clicked()"), 
                     self.changeDimensions)

        self.populateAttributes()
        
        

    ## adds an attribute    
    #  \brief It runs the Attribute Dialog and fetches attribute name and value    
    def addAttribute(self):
        aform  = AttributeDlg()
        if aform.exec_():
            name = aform.name
            value = aform.value
            
            if not aform.name in self.attributes.keys():
                self.attributes[aform.name] = aform.value
                self.populateAttributes(aform.name)
            else:
                QMessageBox.warning(self, "Attribute name exists", "To change the attribute value, please edit the value in the attribute table")
                


    ## changing dimensions of the field
    #  \brief It runs the Dimensions Dialog and fetches rank and dimensions from it
    def changeDimensions(self):
        dform  = DimensionsDlg( self)
        dform.rank = self.rank
        dform.lengths = self.dimensions
        dform.doc = self.dimDoc
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            self.dimDoc = dform.doc
            if self.rank:
                self.dimensions = dform.lengths
            else:    
                self.dimensions = []
            label = self.dimensions.__str__()
            self.dimLabel.setText("Dimensions: %s" % label)
                
                

                
    ## takes a name of the current attribute
    # \returns name of the current attribute            
    def currentTableAttribute(self):
        item = self.attributeTableWidget.item(self.attributeTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()


    ## removes an attribute    
    #  \brief It removes the current attribute asking before about it
    def removeAttribute(self):
        attr = self.currentTableAttribute()
        if attr is None:
            return
        if QMessageBox.question(self, "Attribute - Remove",
                                "Remove attribute: %s = \'%s\'".encode() %  (attr, self.attributes[unicode(attr)]),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        if unicode(attr) in self.attributes.keys():
            del self.attributes[unicode(attr)]
            self.populateAttributes()

    ## changes the current value of the attribute        
    # \brief It changes the current value of the attribute and informs the user that attribute names arenot editable
    def tableItemChanged(self, item):
        attr = self.currentTableAttribute()
        if unicode(attr)  not in self.attributes.keys():
            return
        column = self.attributeTableWidget.currentColumn()
        if column == 1:
            self.attributes[unicode(attr)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Attribute name is not editable", "To change the attribute name, please remove the attribute and add the new one")
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
        for row, name in enumerate(self.attributes):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.attributeTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self.attributes[name])
            self.attributeTableWidget.setItem(row, 1, item2)
            if selectedAttribute is not None and selectedAttribute == name:
                selected = item2
        self.attributeTableWidget.setSortingEnabled(True)
        self.attributeTableWidget.resizeColumnsToContents()
        self.attributeTableWidget.horizontalHeader().setStretchLastSection(True);
        if selected is not None:
            selected.setSelected(True)
            self.attributeTableWidget.setCurrentItem(selected)
            


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_nameLineEdit_textEdited(self, text):
        self.updateUi()

    ## updates field user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
        enable = not self.nameLineEdit.text().isEmpty()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    ## accepts input text strings
    # \brief It copies the field name and type from lineEdit widgets and accept the dialog
    def accept(self):
        self.name = unicode(self.nameLineEdit.text())
        self.nexusType = unicode(self.typeLineEdit.text())
        self.units = unicode(self.unitsLineEdit.text())
        self.value = unicode(self.valueLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())
        
        QDialog.accept(self)

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## field form
    form = FieldDlg()
    form.name = 'distance'
    form.nexusType = 'NX_FLOAT'
    form.units = 'cm'
    form.attributes = {"signal":"1","long_name":"source detector distance", "interpretation":"spectrum"}
    form.doc = """Distance between the source and the mca detector.
It should be defined by client."""
    form.dimensions = [3]
    form.dimDoc = "(x,y,z) coordinates"
    form.value ="1.23,3.43,4.23"
    form.createGUI()
    form.show()
    app.exec_()
    if form.result():
        if form.name:
            print "Field: name = \'%s\'" % ( form.name )
        if form.nexusType:
            print "       type = \'%s\'" % ( form.nexusType )
        if form.units:
            print "       units = \'%s\'" % ( form.units )
        if form.attributes:
            print "Other attributes:"
            for k in form.attributes.keys():
                print  " %s = '%s' " % (k, form.attributes[k])
        if form.value:
            print "Value:\n \'%s\'" % ( form.value )
        if form.rank:
            print " rank = %s" % ( form.rank )
        if form.dimensions:
            print "Dimensions:"
            for row, ln in enumerate(form.dimensions):
                print  " %s: %s " % (row+1, ln)
        if form.dimDoc:
            print "Dimensions Doc: \n%s" % form.dimDoc
            
        if form.doc:
            print "Doc: \n%s" % form.doc
    
