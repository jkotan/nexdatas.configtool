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

from AttributeDlg import AttributeDlg
from NodeDlg import NodeDlg 

## dialog defining a group tag
class GroupDlg(NodeDlg, ui_groupdlg.Ui_GroupDlg):
    
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


    def updateForm(self):

        if self.name is not None:
            self.nameLineEdit.setText(self.name) 
        if self.nexusType is not None:
            self.typeLineEdit.setText(self.nexusType) 
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)

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


    def setFromNode(self, node=None):
        if node:
            self.node = node
        attributeMap = self.node.attributes()
        nNode = self.node.nodeName()

        self.name = attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else ""
        self.nexusType = attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else ""

        self.attributes.clear()    
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = attribute.nodeName()
            if attrName != "name" and attrName != "type":
                self.attributes[unicode(attribute.nodeName())] = unicode(attribute.nodeValue())

        doc = self.node.firstChildElement(QString("doc"))           
        text = self.getText(doc)    
        self.doc = unicode(text).strip() if text else ""
             
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
            item2 =  QTableWidgetItem(self.attributes[name])
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
    def on_typeLineEdit_textEdited(self, text):
        self.updateUi()

    ## updates group user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
        enable = not self.typeLineEdit.text().isEmpty()
        self.applyPushButton.setEnabled(enable)



    ## applys input text strings
    # \brief It copies the group name and type from lineEdit widgets and apply the dialog
    def apply(self):
        self.name = unicode(self.nameLineEdit.text())
        self.nexusType = unicode(self.typeLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())
        
        index = self.view.currentIndex()
        finalIndex = self.model.createIndex(index.row(),2,index.parent().internalPointer())

        if self.node  and self.root and self.node.isElement():
            elem=self.node.toElement()
            
            attributeMap = self.node.attributes()
            for i in range(attributeMap.count()):
                attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
            elem.setAttribute(QString("name"), QString(self.name))
            elem.setAttribute(QString("type"), QString(self.nexusType))

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

        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)
        
if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = GroupDlg()
    form.name = 'entry'
    form.nexusType = 'NXentry'
    form.doc = 'The main entry'
    form.attributes={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.nexusType:
        print "Group: name = \'%s\' type = \'%s\'" % ( form.name, form.nexusType )
    if form.attributes:
        print "Other attributes:"
        for k in form.attributes.keys():
            print  " %s = '%s' " % (k, form.attributes[k])
    if form.doc:
        print "Doc: \n%s" % form.doc
    
