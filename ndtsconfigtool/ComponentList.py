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
## \file ComponentList.py
# Data component list class


""" component list widget """

import os

from PyQt4.QtCore import (Qt, QString, QVariant)
from PyQt4.QtGui import (QWidget, QMenu, QMessageBox, QListWidgetItem)

from .ui.ui_elementlist import Ui_ElementList
from .Component import Component
from .LabeledObject import LabeledObject
from .ElementList import ElementList

## dialog defining a group tag
class ComponentList(ElementList):
    
    ## constructor
    # \param directory element directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ComponentList, self).__init__(parent)

        ## directory from which elements are loaded by default
        self.directory = directory
        
        ## group elements
        self.elements = {}

        ## actions
        self._actions = []
        
        ## show all attribures or only the type attribute
        self._allAttributes = False

        ## user interface
        self.ui = Ui_ElementList()
        
        ## widget title
        self.title = "Components"
        ## element name
        self.name = "components"
        ## class name
        self.clName = "Component"


    ## switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status = None):
        if status is None:
            return self._allAttributes
        self._allAttributes = True if status else False
        for k in self.elements.keys():
            if hasattr(self.elements[k], "instance") \
                    and self.elements[k].instance:
                self.elements[k].instance.viewAttributes(
                    self._allAttributes)
            


    ## removes the current element    
    #  \brief It removes the current element asking before about it
    def removeElement(self, obj = None, question = True):
        super(ComponentList, self).remove(obj, question)

        attr = self.currentListElement()
        if attr is None:
            return
        if QMessageBox.question(
            self, "%s - Remove" % self.clName,
            "Remove %s: %s = \'%s\'".encode() \
                %  (self.clName, attr, self.elements[unicode(attr)]),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return
        if unicode(attr) in self.elements.keys():
            self.elements.pop(unicode(attr))
            self.populateElements()


            
    ## loads the element list from the given dictionary
    # \param itemActions actions of the context menu
    # \param externalActions dictionary with external actions
    def loadList(self, itemActions, externalActions = None):
        actions = externalActions if externalActions else {}
        try:
            dirList = [l for l in os.listdir(self.directory) \
                         if l.endswith(".xml")]
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(),self.name)):
                    self.directory = os.path.abspath(os.path.join(
                            os.getcwd(),self.name))
                else:
                    self.directory = os.getcwd()
                dirList = [l for l in os.listdir(self.directory) \
                               if l.endswith(".xml")]
            except:
                return
            
        for fname in dirList:
            if fname[-4:] == '.xml':
                name = fname[:-4]
            else:
                name = fname
                
            dlg = Component()
            dlg.directory = self.directory
            dlg.name = name
            dlg.createGUI()
            dlg.addContextMenu(itemActions)

            dlg.load()    
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(**actions)    

            el = LabeledObject(name, dlg)
            self.elements[id(el)] =  el
            if el.instance is not None:
                el.instance.id = el.id
            print name
            


    ## sets the elements
    # \param elements dictionary with the elements, i.e. name:xml
    # \param itemActions actions of the tree context menu
    # \param externalActions dictionary with external actions
    def setList(self, elements,  itemActions, externalActions = None):
        actions = externalActions if externalActions else {}
        if not os.path.isdir(self.directory):
            try:
                if os.path.exists(os.path.join(os.getcwd(),self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(),self.name))
                else:
                    self.directory = os.getcwd() 
            except:
                ## todo
                return
            
        for elname in elements.keys():
                
            dlg = Component()
            dlg.directory = self.directory
            dlg.name = elname
            dlg.createGUI()
            dlg.addContextMenu(itemActions)
            try:
                if str(elements[elname]).strip():
                    dlg.set(elements[elname])    
                else:    
                    dlg.createHeader()
                    QMessageBox.warning(
                        self, "%s cannot be loaded" % self.clName,
                        "%s %s without content" % (self.clName, elname))
            except:
                QMessageBox.warning(
                    self, "%s cannot be loaded" % self.clName,
                    "%s %s cannot be loaded" % (self.clName, elname))

                
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(**actions)    

            el = LabeledObject(elname, dlg)
            self.elements[id(el)] =  el
            if el.instance is not None:
                el.instance.id = el.id
            print name
            





if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = ComponentList("../components")
    form.createGUI()
    form.show()
    app.exec_()


    if form.elements:
        print "Other components:"
        for mk in form.elements.keys():
            print  " %s = '%s' " % (mk, form.elements[mk])
    
