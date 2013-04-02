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
## \file RichAttributeDlg.py
# Rich Attribute dialog class

import re
from PyQt4.QtCore import (SIGNAL, QString, QModelIndex)
from PyQt4.QtGui import QMessageBox
from ui.ui_richattributedlg import  Ui_RichAttributeDlg

from NodeDlg import NodeDlg 
from DimensionsDlg import DimensionsDlg

from Errors import CharacterError

## dialog defining an attribute
class RichAttributeDlg(NodeDlg):
    
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
        ## dimensions doc
        self.dimDoc = u''

        ## rank
        self.rank = 0
        ## dimensions
        self.dimensions = []
        self._dimensions = []



        ## allowed subitems
        self.subItems = ["enumeration", "doc", "datasource", "strategy","dimensions"]

        ## user interface
        self.ui = Ui_RichAttributeDlg()


    ## provides the state of the richattribute dialog        
    # \returns state of the richattribute in tuple
    def getState(self):
        dimensions = copy.copy(self.dimensions)

        state = (self.name,
                 self.value,
                 self.nexusType,
                 self.doc,
                 self.dimDoc,
                 self.rank,
                 dimensions
                 )
#        print  "GET", unicode(state)
        return state



    ## sets the state of the richattribute dialog        
    # \param state richattribute state written in tuple 
    def setState(self, state):

        (self.name,
         self.value,
         self.nexusType,
         self.doc,
         self.dimDoc,
         self.rank,
         dimensions
         ) = state
#        print "SET",  unicode(state)
        self.dimensions = copy.copy(dimensions)




    ## updates the richattribute dialog
    # \brief It sets the form local variables 
    def updateForm(self):
        if self.name is not None :
            self.ui.nameLineEdit.setText(self.name) 
        if self.nexusType is not None:
            index = self.ui.typeComboBox.findText(unicode(self.nexusType))
            if  index > -1 :
                self.ui.typeComboBox.setCurrentIndex(index)
                self.ui.otherFrame.hide()
            else:
                index2 = self.ui.typeComboBox.findText('other ...')
                self.ui.typeComboBox.setCurrentIndex(index2)
                self.ui.typeLineEdit.setText(self.nexusType) 
                self.ui.otherFrame.show()
        else:
            index = self.ui.typeComboBox.findText(unicode("None"))
            self.ui.typeComboBox.setCurrentIndex(index)
            self.ui.otherFrame.hide()
        
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)
        if self.value is not None:    
            self.ui.valueLineEdit.setText(self.value)

        if self.rank < len(self.dimensions) :
            self.rank = len(self.dimensions)
        
        if self.dimensions:
            label = self.dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None','*'))
        elif self.rank > 0:
            label = [None for r in range(self.rank)].__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None','*'))
        else:
            self.ui.dimLabel.setText("[]")


        self._dimensions =[]
        for dm in self.dimensions:
            self._dimensions.append(dm)



    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.ui.setupUi(self)

        self.updateForm()

        self._updateUi()

#        self.connect(self.ui.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.resetPushButton, SIGNAL("clicked()"), self.reset)

        self.connect(self.ui.nameLineEdit, SIGNAL("textEdited(QString)"), self._updateUi)
        self.connect(self.ui.typeComboBox, SIGNAL("currentIndexChanged(QString)"), self._currentIndexChanged)
        self.connect(self.ui.dimPushButton, SIGNAL("clicked()"), self._changeDimensions)



    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg
            self.node = node
        attributeMap = self.node.attributes()
        nNode = self.node.nodeName()

        self.name = unicode(attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else "")
        self.nexusType = unicode(attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else "")


        text = self._getText(node)    
        self.value = unicode(text).strip() if text else ""


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



    ## changing dimensions of the field
    #  \brief It runs the Dimensions Dialog and fetches rank and dimensions from it
    def _changeDimensions(self):
        dform  = DimensionsDlg( self)
        dform.rank = self.rank
        dform.lengths = [ln for ln in self._dimensions]
        dform.doc = self.dimDoc
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            self.dimDoc = dform.doc
            if self.rank:
                self._dimensions = [ln for ln in dform.lengths]
            else:    
                self._dimensions = []
            label = self._dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None','*'))



    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def _currentIndexChanged(self, text):
        if text == 'other ...':
            self.ui.otherFrame.show()            
            self.ui.typeLineEdit.setFocus()
        else:
            self.ui.otherFrame.hide()


    ## updates attribute user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        enable = not self.ui.nameLineEdit.text().isEmpty()
        self.ui.applyPushButton.setEnabled(enable)


    ## accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets and accept the dialog
    def apply(self):
        name = unicode(self.ui.nameLineEdit.text())

        try:
            if 1 in [c in name for c in '!"#$%&\'()*+,/;<=>?@[\\]^`{|}~']:
                raise CharacterError, ("Name contains one of forbidden characters") 
            if name[0] == '-':
                raise CharacterError, ("The first character of Name is '-'") 
        except CharacterError, e:   
            QMessageBox.warning(self, "Character Error", unicode(e))
            return

        self.name = name
        self.value = unicode(self.ui.valueLineEdit.text())

        self.nexusType = unicode(self.ui.typeComboBox.currentText())
        if self.nexusType ==  'other ...':
            self.nexusType =  unicode(self.ui.typeLineEdit.text())
        elif self.nexusType ==  'None':    
            self.nexusType =  u'';

        self.doc = unicode(self.ui.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())
        self.view.expand(index)    

        self.dimensions = []
        for dm in self._dimensions:
            self.dimensions.append(dm)



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
        elem.setAttribute(QString("name"), QString(self.name))
        if self.nexusType:
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

        dimens = self.node.firstChildElement(QString("dimensions"))           
        if not self.dimensions and dimens and dimens.nodeName() == "dimensions":
            self._removeElement(dimens,index)
        elif self.dimensions:
            newDimens = self.root.createElement(QString("dimensions"))
            newDimens.setAttribute(QString("rank"), QString(unicode(self.rank)))
            dimDefined = True
            for i in range(min(self.rank,len(self.dimensions))):
                if self.dimensions[i] is None:
                    dimDefined = False
            if dimDefined:
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
