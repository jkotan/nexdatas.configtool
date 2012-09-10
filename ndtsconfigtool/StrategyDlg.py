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
## \file StrategyDlg.py
# Strategy dialog class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_strategydlg

from NodeDlg import NodeDlg 

## dialog defining an attribute
class StrategyDlg(NodeDlg, ui_strategydlg.Ui_StrategyDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(StrategyDlg, self).__init__(parent)
        
        ## strategy mode
        self.mode = u''
        ## trigger label
        self.trigger = u''
        ## postrun  label
        self.postrun = u''
        ## attribute doc
        self.doc = u''

    def updateForm(self):
        index = -1
        if self.mode is not None:
            index = self.modeComboBox.findText(unicode(self.mode))
            if  index > -1 :
                self.modeComboBox.setCurrentIndex(index)
                self.setFrames(self.mode)
        if index < 0 or index is None:        
            index2 = self.modeComboBox.findText(unicode("STEP"))
            self.mode = 'STEP'
            self.modeComboBox.setCurrentIndex(index2)
            self.setFrames(self.mode)
                
        if self.trigger is not None :
            self.triggerLineEdit.setText(self.trigger) 
        if self.postrun is not None :
            self.postLineEdit.setText(self.postrun) 
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)

        self.updateForm()

#        self.connect(self.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), self.reset)


    def setFrames(self, text):
        if text == 'STEP':
            self.triggerFrame.show()            
            self.postFrame.hide()            
            self.triggerLineEdit.setFocus()
        elif text == 'POSTRUN':
            self.postFrame.show()            
            self.triggerFrame.hide()            
            self.postLineEdit.setFocus()
        else:
            self.postFrame.hide()            
            self.triggerFrame.hide()            




    def setFromNode(self, node=None):
        if node:
            self.node = node
        attributeMap = self.node.attributes()

        self.trigger = attributeMap.namedItem("trigger").nodeValue() if attributeMap.contains("trigger") else ""
        self.mode = attributeMap.namedItem("mode").nodeValue() if attributeMap.contains("mode") else ""

        text = self.getText(node)    
        self.postrun = unicode(text).strip() if text else ""

        doc = self.node.firstChildElement(QString("doc"))           
        text = self.getText(doc)    
        self.doc = unicode(text).strip() if text else ""




    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_modeComboBox_currentIndexChanged(self, text):
        self.setFrames(text)


    ## accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets and accept the dialog
    def apply(self):
        class CharacterError(Exception): pass

        self.trigger = ''
        self.postrun = ''

        self.mode = unicode(self.modeComboBox.currentText())
        if self.mode ==  'STEP':
            self.trigger = unicode(self.triggerLineEdit.text())
        if self.mode ==  'POSTRUN':
            self.postrun = unicode(self.postLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.model.createIndex(index.row(),2,index.parent().internalPointer())


        if self.node  and self.root and self.node.isElement():
            elem=self.node.toElement()


            attributeMap = self.node.attributes()
            for i in range(attributeMap.count()):
                attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
            elem.setAttribute(QString("mode"), QString(self.mode))

            if self.mode == 'STEP':
                if self.trigger:
                    elem.setAttribute(QString("trigger"), QString(self.trigger))

            self.replaceText(self.node, index, unicode(self.postrun))

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
    ## attribute form
    form = StrategyDlg()

    form.mode = "pre_sample_flightpath"
    form.trigger = "trigger1"
    form.postrun = 'http://haso.desy.de:/data/power.dat'
    form.doc = "This is the flightpath before the sample position."
    form.createGUI()
    form.show()
    app.exec_()

    if form.mode:
        print "Mode: %s " % ( form.mode )
    if form.mode == "STEP":
        if form.trigger:
            print "Trigger: ", form.trigger
    if form.mode == "POSTRUN":
        if form.postrun:
            print "Postrun label: ", form.postrun
