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
## \file RichAttributeDlg.py
# Rich Attribute dialog class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui.ui_richattributedlg import  Ui_RichAttributeDlg

from NodeDlg import NodeDlg 

## dialog defining an attribute
class RichAttributeDlg(NodeDlg, Ui_RichAttributeDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(RichAttributeDlg, self).__init__(parent)
        
        ## attribute name
        self.name = u''
        ## attribute value
        self.value = u''
        ## attribute type
        self.nexusType = u''
        ## attribute doc
        self.doc = u''

        ## allowed subitems
        self.subItems = ["enumeration", "doc"]





    def updateForm(self):
        if self.name is not None :
            self.nameLineEdit.setText(self.name) 
        if self.nexusType is not None:
            index = self.typeComboBox.findText(unicode(self.nexusType))
            if  index > -1 :
                self.typeComboBox.setCurrentIndex(index)
                self.otherFrame.hide()
            else:
                index2 = self.typeComboBox.findText('other ...')
                self.typeComboBox.setCurrentIndex(index2)
                self.typeLineEdit.setText(self.nexusType) 
                self.otherFrame.show()
        else:
            index = self.typeComboBox.findText(unicode("None"))
            self.typeComboBox.setCurrentIndex(index)
            self.otherFrame.hide()
        
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)
        if self.value is not None:    
            self.valueLineEdit.setText(self.value)


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)

        self.updateForm()

        self.updateUi()

#        self.connect(self.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), self.reset)

    def setFromNode(self, node=None):
        if node:
            self.node = node
        attributeMap = self.node.attributes()
        nNode = self.node.nodeName()

        self.name = unicode(attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else "")
        self.nexusType = unicode(attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else "")


        text = self._getText(node)    
        self.value = unicode(text).strip() if text else ""



        doc = self.node.firstChildElement(QString("doc"))           
        text = self._getText(doc)    
        self.doc = unicode(text).strip() if text else ""



    def getState(self):

        state = (self.name,
                 self.value,
                 self.nexusType,
                 self.doc,
                 )
#        print  "GET", str(state)
        return state



    def setState(self, state):

        (self.name,
         self.value,
         self.nexusType,
         self.doc,
         ) = state
#        print "SET",  str(state)


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_nameLineEdit_textEdited(self, text):
        self.updateUi()


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_typeComboBox_currentIndexChanged(self, text):
        if text == 'other ...':
            self.otherFrame.show()            
            self.typeLineEdit.setFocus()
        else:
            self.otherFrame.hide()

    ## updates attribute user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
        enable = not self.nameLineEdit.text().isEmpty()
        self.applyPushButton.setEnabled(enable)

    ## accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets and accept the dialog
    def apply(self):
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

        self.nexusType = unicode(self.typeComboBox.currentText())
        if self.nexusType ==  'other ...':
            self.nexusType =  unicode(self.typeLineEdit.text())
        elif self.nexusType ==  'None':    
            self.nexusType =  u'';

        self.doc = unicode(self.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())

        if self.node  and self.root and self.node.isElement():
            self.updateNode(index)
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)


    def updateNode(self,index=QModelIndex()):
        elem=self.node.toElement()


        attributeMap = self.node.attributes()
        for i in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
        elem.setAttribute(QString("name"), QString(self.name))
        elem.setAttribute(QString("type"), QString(self.nexusType))

        self._replaceText(self.node, index, unicode(self.value))

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

                    


if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## attribute form
    form = RichAttributeDlg()
    form.name = "pre_sample_flightpath"
    form.nexusType = 'NX_FLOAT'
    form.doc = "This is the flightpath before the sample position."
    form.value = "1.2"
    form.createGUI()
    form.show()
    app.exec_()

    if form.name:
        print "Attribute: %s = \'%s\'" % ( form.name, form.value )
    if form.nexusType:
        print "Type: %s" % form.nexusType
    if form.doc:
        print "Doc: \n%s" % form.doc
