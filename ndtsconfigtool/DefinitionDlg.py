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
## \file DefinitionDlg.py
# Definition dialog class

import re
from PyQt4.QtCore import (SIGNAL, QString, Qt, QVariant, QModelIndex)
from PyQt4.QtGui import (QMessageBox, QTableWidgetItem)
from ui.ui_definitiondlg import  Ui_DefinitionDlg

import copy 

from AttributeDlg import AttributeDlg
from NodeDlg import NodeDlg 

## dialog defining a definition tag
class DefinitionDlg(NodeDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DefinitionDlg, self).__init__(parent)
        
        ## definition name
        self.name = u''
        ## definition type
        self.nexusType = u''
        ## definition doc
        self.doc = u''
        ## definition attributes
        self.attributes = {}
        self.__attributes = {}

        ## allowed subitems
        self.subItems = ["group", "field", "attribute", "link", "component", "doc", "symbols"]

        ## user interface
        self.ui = Ui_DefinitionDlg()



    ## updates the definition dialog
    # \brief It sets the form local variables
    def updateForm(self):

        if self.name is not None:
            self.ui.nameLineEdit.setText(self.name) 
        if self.nexusType is not None:
            self.ui.typeLineEdit.setText(self.nexusType) 
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)


        self.__attributes.clear()
        for at in self.attributes.keys():
            self.__attributes[unicode(at)]=self.attributes[(unicode(at))]

        self.populateAttributes()
        


        
    ## provides the state of the definition dialog        
    # \returns state of the definition in tuple
    def getState(self):
        attributes = copy.copy(self.attributes)

        state = (self.name,
                 self.nexusType,
                 self.doc,
                 attributes
                 )
#        print  "GET", unicode(state)
        return state



    ## sets the state of the definition dialog        
    # \param state definition state written in tuple 
    def setState(self, state):

        (self.name,
         self.nexusType,
         self.doc,
         attributes
         ) = state
#        print "SET",  unicode(state)
        self.attributes = copy.copy(attributes)



    ##  creates GUI
    # \brief It calls ui.setupUi(self),  updateForm() and connects signals and slots    
    def createGUI(self):
        self.ui.setupUi(self)
        
        self.updateForm()

        self.__updateUi()

#        self.connect(self.ui.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.resetPushButton, SIGNAL("clicked()"), self.reset)
        self.connect(self.ui.attributeTableWidget, SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.__tableItemChanged)
        self.connect(self.ui.addPushButton, SIGNAL("clicked()"), self.__addAttribute)
        self.connect(self.ui.removePushButton, SIGNAL("clicked()"), self.__removeAttribute)

#        self.connect(self.ui.typeLineEdit, SIGNAL("textEdited(QString)"), self.__updateUi)


    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg class
            self.node = node
        if not self.node:
            ## exception?
            return
        attributeMap = self.node.attributes()
        nNode = unicode(self.node.nodeName())

        self.name = unicode(attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else "")
        self.nexusType = unicode(attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else "")

        self.attributes.clear()    
        self.__attributes.clear()    
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = unicode(attribute.nodeName())
            if attrName != "name" and attrName != "type":
                self.attributes[attrName] = unicode(attribute.nodeValue())
                self.__attributes[attrName] = unicode(attribute.nodeValue())

        doc = self.node.firstChildElement(QString("doc"))           
        text = self.dts.getText(doc)    
        self.doc = unicode(text).strip() if text else ""

             
    ## adds an attribute    
    #  \brief It runs the Definition Dialog and fetches attribute name and value    
    def __addAttribute(self):
        aform  = AttributeDlg()
        if aform.exec_():
            name = aform.name
            value = aform.value
            
            if not aform.name in self.__attributes.keys():
                self.__attributes[aform.name] = aform.value
                self.populateAttributes(aform.name)
            else:
                QMessageBox.warning(self, "Attribute name exists", "To change the attribute value, please edit the value in the attribute table")
                
                
    ## takes a name of the current attribute
    # \returns name of the current attribute            
    def __currentTableAttribute(self):
        item = self.ui.attributeTableWidget.item(self.ui.attributeTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()


    ## removes an attribute    
    #  \brief It removes the current attribute asking before about it
    def __removeAttribute(self):
        attr = self.__currentTableAttribute()
        if attr is None:
            return
        if QMessageBox.question(self, "Attribute - Remove",
                                "Remove attribute: %s = \'%s\'".encode() %  (attr, self.__attributes[unicode(attr)]),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return
        if unicode(attr) in self.__attributes.keys():
            self.__attributes.pop(unicode(attr))
            self.populateAttributes()


    ## changes the current value of the attribute        
    # \brief It changes the current value of the attribute and informs the user that attribute names arenot editable
    def __tableItemChanged(self, item):
        attr = self.__currentTableAttribute()
        if unicode(attr)  not in self.__attributes.keys():
            return
        column = self.ui.attributeTableWidget.currentColumn()
        if column == 1:
            self.__attributes[unicode(attr)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Attribute name is not editable", "To change the attribute name, please remove the attribute and add the new one")
        self.populateAttributes()


    ## fills in the attribute table      
    # \param selectedAttribute selected attribute    
    def populateAttributes(self, selectedAttribute = None):
        selected = None
        self.ui.attributeTableWidget.clear()
        self.ui.attributeTableWidget.setSortingEnabled(False)
        self.ui.attributeTableWidget.setRowCount(len(self.__attributes))
        headers = ["Name", "Value"]
        self.ui.attributeTableWidget.setColumnCount(len(headers))
        self.ui.attributeTableWidget.setHorizontalHeaderLabels(headers)	
        for row, name in enumerate(self.__attributes):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.ui.attributeTableWidget.setItem(row, 0, item)
            item2 =  QTableWidgetItem(self.__attributes[name])
            self.ui.attributeTableWidget.setItem(row, 1, item2)
            if selectedAttribute is not None and selectedAttribute == name:
                selected = item2
        self.ui.attributeTableWidget.setSortingEnabled(True)
        self.ui.attributeTableWidget.resizeColumnsToContents()
        self.ui.attributeTableWidget.horizontalHeader().setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.attributeTableWidget.setCurrentItem(selected)
            


    ## updates definition user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        pass
#        enable = not self.ui.typeLineEdit.text().isEmpty()
#        self.ui.applyPushButton.setEnabled(enable)



    ## applys input text strings
    # \brief It copies the definition name and type from lineEdit widgets and apply the dialog
    def apply(self):
        self.name = unicode(self.ui.nameLineEdit.text())
        self.nexusType = unicode(self.ui.typeLineEdit.text())

        self.doc = unicode(self.ui.docTextEdit.toPlainText())
        
        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())

        self.attributes.clear()
        for at in self.__attributes.keys():
            self.attributes[at] = self.__attributes[at]

        self.view.expand(index)    
        if self.node  and self.root and self.node.isElement():
            self.updateNode(index)

        if  index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)
        self.view.expand(index)    


    ## updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self,index=QModelIndex()):
        elem=self.node.toElement()
            
        attributeMap = self.node.attributes()
        for i in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(0).nodeName())
        if self.name:    
            elem.setAttribute(QString("name"), QString(self.name))
        if self.nexusType:
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

        
if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## definition form
    form = DefinitionDlg()
    form.name = 'entry'
    form.nexusType = 'NXentry'
    form.doc = 'The main entry'
    form.attributes={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.nexusType:
        print "Definition: name = \'%s\' type = \'%s\'" % ( form.name, form.nexusType )
    if form.attributes:
        print "Other attributes:"
        for k in form.attributes.keys():
            print  " %s = '%s' " % (k, form.attributes[k])
    if form.doc:
        print "Doc: \n%s" % form.doc
    
