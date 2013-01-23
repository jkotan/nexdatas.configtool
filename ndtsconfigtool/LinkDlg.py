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
## \file LinkDlg.py
# Link dialog class

import re
from PyQt4.QtCore import (SIGNAL, QString, QModelIndex)
from PyQt4.QtGui import (QMessageBox)
from ui.ui_linkdlg import Ui_LinkDlg

from NodeDlg import NodeDlg 

## dialog defining a tag link 
class LinkDlg(NodeDlg, Ui_LinkDlg):
    
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

        ## allowed subitems
        self.subItems=[ "doc"]



    ## updates the link dialog
    # \brief It sets the form local variables
    def updateForm(self):
        if self.name is not None:
            self.nameLineEdit.setText(self.name) 
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)

        if self.target is not None:    
            self.targetLineEdit.setText(self.target)

        if self.node:    
            doc = self.node.firstChildElement(QString("doc"))           
            text = self._getText(doc)    
        else:
            text = ""
        self.doc = unicode(text).strip() if text else ""


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.setupUi(self)
        self.targetToolButton.setEnabled(False)

        self.updateForm()

        self._updateUi()


        #        self.connect(self.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), self.reset)
        self.connect(self.nameLineEdit, SIGNAL("textEdited(QString)"), self._updateUi)


    ## provides the state of the link dialog        
    # \returns state of the group in tuple
    def getState(self):

        state = (self.name,
                 self.target,
                 self.doc
                 )
#        print  "GET", unicode(state)
        return state



    ## sets the state of the link dialog        
    # \param state link state written in tuple 
    def setState(self, state):

        (self.name,
         self.target,
         self.doc
         ) = state
#        print "SET",  unicode(state)



    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg
            self.node = node
        attributeMap = self.node.attributes()
        nNode = unicode(self.node.nodeName())

        self.name = unicode(attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else "")
        self.target = unicode(attributeMap.namedItem("target").nodeValue() if attributeMap.contains("target") else "")
 
        doc = self.node.firstChildElement(QString("doc"))           
        text = self._getText(doc)    
        self.doc = unicode(text).strip() if text else ""



    ## updates link user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
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
        finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())
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
            attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
        if self.name:    
            elem.setAttribute(QString("name"), QString(self.name))
        if self.target:    
            elem.setAttribute(QString("target"), QString(self.target))


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
    from PyQt4.QtGui import QApplication

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
    
