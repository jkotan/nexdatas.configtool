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

from NodeDlg import NodeDlg 

## dialog defining a tag link 
class LinkDlg(NodeDlg, ui_linkdlg.Ui_LinkDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(LinkDlg, self).__init__(parent)
        
        ## link name
        self.name = u''
        ## link target
        self.target = u''
        ## field doc
        self.doc = u''

    def updateForm(self):
        if self.name is not None:
            self.nameLineEdit.setText(self.name) 
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)

        if self.target is not None:    
            self.targetLineEdit.setText(self.target)

        doc = self.node.firstChildElement(QString("doc"))           
        text = self.getText(doc)    
        self.doc = unicode(text).strip() if text else ""


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

    def setFromNode(self, node=None):
        if node:
            self.node = node
        attributeMap = self.node.attributes()
        nNode = self.node.nodeName()

        self.name = attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else ""
        self.target = attributeMap.namedItem("target").nodeValue() if attributeMap.contains("target") else ""
 
        doc = self.node.firstChildElement(QString("doc"))           
        text = self.getText(doc)    
        self.doc = unicode(text).strip() if text else ""

    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_nameLineEdit_textEdited(self, text):
        self.updateUi()

    ## updates link user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self):
        enable = not self.nameLineEdit.text().isEmpty()
        self.applyPushButton.setEnabled(enable)



    ## accepts input text strings
    # \brief It copies the link name and target from lineEdit widgets and accept the dialog
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
        self.target = unicode(self.targetLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.model.createIndex(index.row(),2,index.parent().internalPointer())

        if self.node  and self.root and self.node.isElement():
            elem=self.node.toElement()


            attributeMap = self.node.attributes()
            for i in range(attributeMap.count()):
                attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
            elem.setAttribute(QString("name"), QString(self.name))
            elem.setAttribute(QString("target"), QString(self.target))


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
    ## link form
    form = LinkDlg()
    form.name = 'data'
    form.target = '/NXentry/NXinstrument/NXdetector/data'
    form.createGUI()
    form.show()
    app.exec_()

    if form.name:
        print "Link: %s = \'%s\'" % ( form.name, form.target )
    
