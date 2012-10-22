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
from PyQt4.QtCore import (SIGNAL, QString, QVariant, Qt, QModelIndex)
from PyQt4.QtGui import (QMessageBox, QTableWidgetItem)
from ui.ui_fielddlg import Ui_FieldDlg
from PyQt4.QtXml import (QDomDocument, QDomNode)


from AttributeDlg import AttributeDlg
from DimensionsDlg import DimensionsDlg

import copy

from NodeDlg import NodeDlg 

## dialog defining a field tag
class FieldDlg(NodeDlg, Ui_FieldDlg):
    
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
        self._attributes = {}

        ## rank
        self.rank = 0
        ## dimensions
        self.dimensions = []
        self._dimensions = []


        ## allowed subitems
        self.subItems = ["attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"]


    ## provides the state of the field dialog        
    # \returns state of the field in tuple
    def getState(self):
        attributes = copy.copy(self.attributes)
        dimensions = copy.copy(self.dimensions)

        state = (self.name,
                 self.nexusType,
                 self.units,
                 self.value,
                 self.doc,
                 self.dimDoc,
                 attributes,
                 dimensions
                 )
#        print  "GET", str(state)
        return state



    ## sets the state of the field dialog        
    # \param state field state written in tuple 
    def setState(self, state):

        (self.name,
         self.nexusType,
         self.units,
         self.value,
         self.doc,
         self.dimDoc,
         attributes,
         dimensions
         ) = state
#        print "SET",  str(state)
        self.attributes = copy.copy(attributes)
        self.dimensions = copy.copy(dimensions)


    ## updates the field dialog
    # \brief It sets the form local variables 
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

        self._dimensions =[]
        for dm in self.dimensions:
            self._dimensions.append(dm)

        self._attributes.clear()
        for at in self.attributes.keys():
            self._attributes[unicode(at)]=self.attributes[(unicode(at))]

        self.populateAttributes()


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)

        self.updateForm()

        self._updateUi()

#       self.connect(self.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), self.reset)
        self.connect(self.attributeTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"), self._tableItemChanged)
        self.connect(self.addPushButton, SIGNAL("clicked()"), self._addAttribute)
        self.connect(self.removePushButton, SIGNAL("clicked()"), self._removeAttribute)
        self.connect(self.dimPushButton, SIGNAL("clicked()"), self._changeDimensions)

        self.connect(self.nameLineEdit, SIGNAL("textEdited(QString)"), self._updateUi)

        self.populateAttributes()

        
    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg
            self.node = node
        attributeMap = self.node.attributes()
        nNode = unicode(self.node.nodeName())

        self.name = unicode(attributeMap.namedItem("name").nodeValue() \
                                if attributeMap.contains("name") else "")
        self.nexusType = unicode(attributeMap.namedItem("type").nodeValue() \
                                     if attributeMap.contains("type") else "")
        self.units = unicode(attributeMap.namedItem("units").nodeValue() \
                                 if attributeMap.contains("units") else "")

        text = self._getText(self.node)    
        self.value = unicode(text).strip() if text else ""

        self.attributes.clear()    
        self._attributes.clear()    
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = unicode(attribute.nodeName())
            if attrName != "name" and attrName != "type" and attrName != "units":
                self.attributes[attrName] = unicode(attribute.nodeValue())
                self._attributes[attrName] = unicode(attribute.nodeValue())


        dimens = self.node.firstChildElement(QString("dimensions"))           
        attributeMap = dimens.attributes()

        self.dimensions = []
        self._dimensions = []
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
                            self._dimensions.append(None)
                        self._dimensions[index-1] = value     
                        self.dimensions[index-1] = value     

                child = child.nextSibling()

        if self.rank < len(self.dimensions) :
            self.rank = len(self.dimensions)
            self.rank = len(self._dimensions)

        doc = self.node.firstChildElement(QString("doc"))           
        text = self._getText(doc)    
        self.doc = unicode(text).strip() if text else ""




    ## adds an attribute    
    #  \brief It runs the Field Dialog and fetches attribute name and value    
    def _addAttribute(self):
        aform  = AttributeDlg()
        if aform.exec_():
            name = aform.name
            value = aform.value
            
            if not aform.name in self._attributes.keys():
                self._attributes[aform.name] = aform.value
                self.populateAttributes(aform.name)
            else:
                QMessageBox.warning(self, "Attribute name exists", "To change the attribute value, please edit the value in the attribute table")
                


    ## changing dimensions of the field
    #  \brief It runs the Dimensions Dialog and fetches rank and dimensions from it
    def _changeDimensions(self):
        dform  = DimensionsDlg( self)
        dform.rank = self.rank
        dform.lengths = self._dimensions
        dform.doc = self.dimDoc
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            self.dimDoc = dform.doc
            if self.rank:
                self._dimensions = dform.lengths
            else:    
                self._dimensions = []
            label = self._dimensions.__str__()
            self.dimLabel.setText("%s" % label)
                
                

                
    ## takes a name of the current attribute
    # \returns name of the current attribute            
    def _currentTableAttribute(self):
        item = self.attributeTableWidget.item(self.attributeTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()


    ## removes an attribute    
    #  \brief It removes the current attribute asking before about it
    def _removeAttribute(self):
        attr = self._currentTableAttribute()
        if attr is None:
            return
        if QMessageBox.question(self, "Attribute - Remove",
                                "Remove attribute: %s = \'%s\'".encode() %  (attr, self._attributes[unicode(attr)]),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        if unicode(attr) in self._attributes.keys():
            self._attributes.pop(unicode(attr))
            self.populateAttributes()

    ## changes the current value of the attribute        
    # \brief It changes the current value of the attribute and informs the user that attribute names arenot editable
    def _tableItemChanged(self, item):
        attr = self._currentTableAttribute()
        if unicode(attr)  not in self._attributes.keys():
            return
        column = self.attributeTableWidget.currentColumn()
        if column == 1:
            self._attributes[unicode(attr)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Attribute name is not editable", "To change the attribute name, please remove the attribute and add the new one")
        self.populateAttributes()

    ## fills in the attribute table      
    # \param selectedAttribute selected attribute    
    def populateAttributes(self, selectedAttribute = None):
        selected = None
        self.attributeTableWidget.clear()
        self.attributeTableWidget.setSortingEnabled(False)
        self.attributeTableWidget.setRowCount(len(self._attributes))
        headers = ["Name", "Value"]
        self.attributeTableWidget.setColumnCount(len(headers))
        self.attributeTableWidget.setHorizontalHeaderLabels(headers)	
        for row, name in enumerate(self._attributes):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.attributeTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self._attributes[name])
            self.attributeTableWidget.setItem(row, 1, item2)
            if selectedAttribute is not None and selectedAttribute == name:
                selected = item2
        self.attributeTableWidget.setSortingEnabled(True)
        self.attributeTableWidget.resizeColumnsToContents()
        self.attributeTableWidget.horizontalHeader().setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.attributeTableWidget.setCurrentItem(selected)
            

    ## updates field user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        enable = not self.nameLineEdit.text().isEmpty()
        self.applyPushButton.setEnabled(enable)


    ## appends node
    # \param node DOM node to remove
    # \param parent parent DOM node        
    def appendNode(self, node, parent):
        if node.nodeName() == 'datasource' :
            if not self.node:
                return
            child = self.node.firstChild()
            while not child.isNull():
                if child.nodeName() == 'datasource':
                    QMessageBox.warning(self, "DataSource exists", 
                                        "To add a new datasource please remove the old one")
                    return
                child = child.nextSibling()    
        NodeDlg.appendNode(self, node, parent)       


    ## applys input text strings
    # \brief It copies the field name and type from lineEdit widgets and apply the dialog
    def apply(self):
        self.name = unicode(self.nameLineEdit.text())
        self.nexusType = unicode(self.typeLineEdit.text())
        self.units = unicode(self.unitsLineEdit.text())
        self.value = unicode(self.valueLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())


        self.attributes.clear()
        for at in self._attributes.keys():
            self.attributes[at] = self._attributes[at]

        self.dimensions = []
        for dm in self._dimensions:
            self.dimensions.append(dm)

        if self.node  and self.root and self.node.isElement():
            self.updateNode(index)
                    
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)

        
    ## updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self,index=QModelIndex()):
        elem=self.node.toElement()


        attributeMap = self.node.attributes()
        for i in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
        elem.setAttribute(QString("name"), QString(self.name))
        elem.setAttribute(QString("type"), QString(self.nexusType))
        elem.setAttribute(QString("units"), QString(self.units))

        self._replaceText(self.node, index, unicode(self.value))
        
        for attr in self.attributes.keys():
            elem.setAttribute(QString(attr), QString(self.attributes[attr]))

        doc = self.node.firstChildElement(QString("doc"))           
        if not self.doc and doc and doc.nodeName() == "doc" :
            self._removeElement(doc, index)
        elif self.doc:
            newDoc = self.root.createElement(QString("doc"))
            newText = self.root.createTextNode(QString(self.doc))
            newDoc.appendChild(newText)
            if doc and doc.nodeName() == "doc" :
                self._replaceElement(doc, newDoc, index)
            else:
                self._appendElement(newDoc, index)

        dimens = self.node.firstChildElement(QString("dimensions"))           
        if not self.dimensions and dimens and dimens.nodeName() == "dimensions":
            self._removeElement(dimens,index)
        elif self.dimensions:
            newDimens = self.root.createElement(QString("dimensions"))
            newDimens.setAttribute(QString("rank"), QString(unicode(self.rank)))
            for i in range(min(self.rank,len(self.dimensions))):
                dim = self.root.createElement(QString("dim"))
                dim.setAttribute(QString("index"), QString(unicode(i+1)))
                dim.setAttribute(QString("value"), QString(unicode(self.dimensions[i])))
                newDimens.appendChild(dim)
            if dimens and dimens.nodeName() == "dimensions" :
                self._replaceElement(dimens, newDimens, index)
            else:
                self._appendElement(newDimens, index)



if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

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
    
