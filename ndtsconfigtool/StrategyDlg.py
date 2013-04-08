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
## \file StrategyDlg.py
# Strategy dialog class

import re
from PyQt4.QtCore import (SIGNAL, QString, QModelIndex)
from ui.ui_strategydlg import Ui_StrategyDlg

from NodeDlg import NodeDlg 

## dialog defining an attribute
class StrategyDlg(NodeDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(StrategyDlg, self).__init__(parent)
        
        ## strategy mode
        self.mode = u''
        ## trigger label
        self.trigger = u''
        ## growing dimension
        self.grows = u''
        ## postrun  label
        self.postrun = u''
        ## attribute doc
        self.doc = u''
        ## compression flag
        self.compression = False
        ## compression rate
        self.rate = 5
        ## compression shuffle
        self.shuffle = True

        ## user interface
        self.ui = Ui_StrategyDlg()

    ## updates the field strategy
    # \brief It sets the form local variables 
    def updateForm(self):
        index = -1
        if self.mode is not None:
            index = self.ui.modeComboBox.findText(unicode(self.mode))
            if  index > -1 :
                self.ui.modeComboBox.setCurrentIndex(index)
                self.setFrames(self.mode)
        if index < 0 or index is None:        
            index2 = self.ui.modeComboBox.findText(unicode("STEP"))
            self.mode = 'STEP'
            self.ui.modeComboBox.setCurrentIndex(index2)
            self.setFrames(self.mode)
                
        if self.trigger is not None :
            self.ui.triggerLineEdit.setText(self.trigger) 

        self.ui.compressionCheckBox.setChecked(self.compression) 
        self.ui.shuffleCheckBox.setChecked(self.shuffle) 
        self.ui.rateSpinBox.setValue(self.rate)

        if self.grows is not None :
            try:
                grows = int(self.grows)
                print "GROWS", grows
                if grows < 0:
                    grows = 0
            except:
                grows = 0
            self.ui.growsSpinBox.setValue(grows) 
        if self.postrun is not None :
            self.ui.postLineEdit.setText(self.postrun) 
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.ui.setupUi(self)

        self.updateForm()

#        self.connect(self.ui.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.resetPushButton, SIGNAL("clicked()"), self.reset)
        self.connect(self.ui.modeComboBox, SIGNAL("currentIndexChanged(QString)"), self.setFrames)
        self.connect(self.ui.compressionCheckBox, SIGNAL("stateChanged(int)"), self.setCompression)

        self.setCompression(self.ui.compressionCheckBox.isChecked())


    ## provides the state of the strategy dialog        
    # \returns state of the strategy in tuple
    def getState(self):
        state = (self.mode,
                 self.trigger,
                 self.grows,
                 self.postrun,
                 self.compression,
                 self.rate,
                 self.shuffle,
                 self.doc
                 )
#        print  "GET", unicode(state)
        return state


    ## sets the state of the strategy dialog        
    # \param state strategy state written in tuple 
    def setState(self, state):

        (self.name,
         self.trigger,
         self.grows,
         self.postrun,
         self.compression,
         self.rate,
         self.shuffle,
         self.doc
         ) = state
#        print "SET",  unicode(state)


    ## shows and hides frames according to modeComboBox
    # \param text the edited text   
    def setFrames(self, text):
        if text == 'STEP':
            self.ui.triggerFrame.show()            
            self.ui.postFrame.hide()            
            self.ui.triggerLineEdit.setFocus()
        elif text == 'POSTRUN':
            self.ui.postFrame.show()            
            self.ui.triggerFrame.hide()            
            self.ui.postLineEdit.setFocus()
        else:
            self.ui.postFrame.hide()            
            self.ui.triggerFrame.hide()            


    ## shows and hides compression widgets according to compressionCheckBox
    # \param state value from compressionCheckBox
    def setCompression(self, state):
        enable = bool(state)
        self.ui.rateLabel.setEnabled(enable)
        self.ui.rateSpinBox.setEnabled(enable)
        self.ui.shuffleCheckBox.setEnabled(enable)
                



    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg class
            self.node = node
        attributeMap = self.node.attributes()

        self.trigger = attributeMap.namedItem("trigger").nodeValue() if attributeMap.contains("trigger") else ""
        self.grows = attributeMap.namedItem("grows").nodeValue() if attributeMap.contains("grows") else ""
        self.mode = attributeMap.namedItem("mode").nodeValue() if attributeMap.contains("mode") else ""

        if attributeMap.contains("compression"):
            self.compression = \
                False if str(attributeMap.namedItem("compression").nodeValue()).upper() == "FALSE"  else True

            if attributeMap.contains("shuffle"):
                self.shuffle = \
                    False if str(attributeMap.namedItem("shuffle").nodeValue()).upper() == "FALSE"  else True

            if attributeMap.contains("rate"):
                rate = int(attributeMap.namedItem("rate").nodeValue())
                if rate < 0:
                    rate = 0
                elif rate > 9:
                    rate = 9
                self.rate = rate    


        text = self.dts.getText(node)    
        self.postrun = unicode(text).strip() if text else ""

        doc = self.node.firstChildElement(QString("doc"))           
        text = self.dts.getText(doc)    
        self.doc = unicode(text).strip() if text else ""




    ## accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets and accept the dialog
    def apply(self):

        self.trigger = ''
        self.grows = ''
        self.postrun = ''

        self.mode = unicode(self.ui.modeComboBox.currentText())
        if self.mode ==  'STEP':
            self.trigger = unicode(self.ui.triggerLineEdit.text())
            grows = int(self.ui.growsSpinBox.value())
            if grows > 0:
                self.grows= str(grows)
        if self.mode ==  'POSTRUN':
            self.postrun = unicode(self.ui.postLineEdit.text())


        self.compression = self.ui.compressionCheckBox.isChecked()
        self.shuffle = self.ui.shuffleCheckBox.isChecked()
        self.rate = self.ui.rateSpinBox.value()
            

        print "cP", self.compression

        self.doc = unicode(self.ui.docTextEdit.toPlainText())

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
            attributeMap.removeNamedItem(attributeMap.item(0).nodeName())
        elem.setAttribute(QString("mode"), QString(self.mode))

        if self.mode == 'STEP':
            if self.trigger:
                elem.setAttribute(QString("trigger"), QString(self.trigger))
            if self.grows:
                elem.setAttribute(QString("grows"), QString(self.grows))
        if self.compression:
            elem.setAttribute(QString("compression"), QString("true"))
            elem.setAttribute(QString("shuffle"), QString("true") if self.shuffle else "false" )
            elem.setAttribute(QString("rate"), QString(str(self.rate)))

        self._replaceText(index, unicode(self.postrun))

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
