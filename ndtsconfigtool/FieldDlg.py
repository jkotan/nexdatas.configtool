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
from PyQt4.QtXml import (QDomDocument, QDomNode)


from AttributeDlg import AttributeDlg
from DimensionsDlg import DimensionsDlg


from NodeDlg import NodeDlg 

## dialog defining a field tag
class FieldDlg(NodeDlg, ui_fielddlg.Ui_FieldDlg):
    
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





    def updateForm(self):
        if self.name is not None:
            self.nameLineEdit.setText(self.name) 
        if self.nexusType is not None:
            self.typeLineEdit.setText(self.nexusType) 
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)
        if self.units is not None:    
            self.unitsLineEdit.setText(self.units)
        if self.value is not None:    
            self.valueLineEdit.setText(self.value)

        if self.rank < len(self.dimensions) :
            self.rank = len(self.dimensions)
        
        if self.dimensions:
            label = self.dimensions.__str__()
            self.dimLabel.setText("%s" % label)

        self.populateAttributes()


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)

        self.updateForm()

        self.updateUi()

        self.connect(self.applyPushButton, SIGNAL("clicked()"), 
                     self.apply)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), 
                     self.reset)
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

        
    def setFromNode(self, node=None):
        if node:
            self.node = node
        attributeMap = self.node.attributes()
        nNode = self.node.nodeName()

        if attributeMap.contains("name"):
            self.name = attributeMap.namedItem("name").nodeValue()
        else:
            self.name = ""

        if attributeMap.contains("type"):
            self.nexusType = attributeMap.namedItem("type").nodeValue() 
        else:
            self.nexusType = ""


        if attributeMap.contains("units"):
            self.units = attributeMap.namedItem("units").nodeValue() 
        else:
            self.units = ""



        text = self.getText(node)    
        if text:
            self.value = unicode(text).strip()
        else:
            self.value = ""



        self.attributes.clear()    
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = attribute.nodeName()
            if attrName != "name" and attrName != "type" and attrName != "units":
                self.attributes[unicode(attribute.nodeName())] = unicode(attribute.nodeValue())


        dimens = self.node.firstChildElement(QString("dimensions"))           
        attributeMap = dimens.attributes()

        self.dimensions = []
        if attributeMap.contains("rank"):
            try:
                self.rank = int(attributeMap.namedItem("rank").nodeValue())
                if self.rank < 0: 
                    self.rank = 0
            except:
                self.rank = 0
        else:
            self.rank = 0
        if self.rank > 0:
            child = dimens.firstChild()
            maxIndex = 0
            lengths = {}
            while not child.isNull():
                if child.isElement() and child.nodeName() == "dim":
                    attributeMap = child.attributes()
                    index = None
                    value = None
                    try:                        
                        if attributeMap.contains("index"):
                            index = int(attributeMap.namedItem("index").nodeValue())
                        if attributeMap.contains("value"):
                            value = int(attributeMap.namedItem("value").nodeValue())
                    except:
                        pass
                    if index < 1: index = None
                    if value < 1: value = None
                    if index is not None:
                        while len(self.dimensions)< index:
                            self.dimensions.append(None)
                        self.dimensions[index-1] = value     

                child = child.nextSibling()

        if self.rank < len(self.dimensions) :
            self.rank = len(self.dimensions)

        doc = self.node.firstChildElement(QString("doc"))           
        if doc:
            self.doc =unicode(doc.text()).strip()

        else:
            self.doc = ""


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
            self.dimLabel.setText("%s" % label)
                
                

                
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
            self.attributes.pop(unicode(attr))
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
        self.attributeTableWidget.horizontalHeader().setStretchLastSection(True)
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
        self.applyPushButton.setEnabled(enable)

    ## applys input text strings
    # \brief It copies the field name and type from lineEdit widgets and apply the dialog
    def apply(self):
        self.name = unicode(self.nameLineEdit.text())
        self.nexusType = unicode(self.typeLineEdit.text())
        self.units = unicode(self.unitsLineEdit.text())
        self.value = unicode(self.valueLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())

        index = self.view.currentIndex()

        if self.node  and self.root and self.node.isElement():
            elem=self.node.toElement()


            attributeMap = self.node.attributes()
            for i in range(attributeMap.count()):
                attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
            elem.setAttribute(QString("name"), QString(self.name))
            elem.setAttribute(QString("type"), QString(self.nexusType))
            elem.setAttribute(QString("units"), QString(self.units))

            self.replaceText(self.node, index ,unicode(self.value))

            for attr in self.attributes.keys():
                elem.setAttribute(QString(attr), QString(self.attributes[attr]))

            doc = self.node.firstChildElement(QString("doc"))           
            if not self.doc and doc and doc.nodeName() == "doc" :
                self.removeElement(doc, index)
            elif self.doc:
                newDoc = self.root.createElement(QString("doc"))
                newText = self.root.createTextNode(QString(self.doc))
                newDoc.appendChild(newText)
                if doc and doc.nodeName() == "doc" :
                    self.replaceElement(doc, newDoc, index)
                else:
                    self.appendElement(newDoc, index)

            dimens = self.node.firstChildElement(QString("dimensions"))           
            if not self.dimensions and dimens and dimens.nodeName() == "dimensions":
                self.removeElement(dimens,index)
            elif self.dimensions:
                newDimens = self.root.createElement(QString("dimensions"))
                newDimens.setAttribute(QString("rank"), QString(unicode(self.rank)))
                for i in range(min(self.rank,len(self.dimensions))):
                    dim = self.root.createElement(QString("dim"))
                    dim.setAttribute(QString("index"), QString(unicode(i+1)))
                    dim.setAttribute(QString("value"), QString(unicode(self.dimensions[i])))
                    newDimens.appendChild(dim)
                if dimens and dimens.nodeName() == "doc" :
                    self.replaceElement(dimens, newDimens, index)
                else:
                    self.appendElement(newDimens, index)

                    
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)



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
    
