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
## \file ElementList.py
# Data source list class

""" datasource list widget """
import os

from PyQt4.QtCore import (Qt, QString, QVariant)
from PyQt4.QtGui import (QWidget, QMenu, QMessageBox, QListWidgetItem)

from .ui.ui_elementlist import Ui_ElementList
from .LabeledObject import LabeledObject

## dialog defining a group tag
class ElementList(QWidget):
    
    ## constructor
    # \param directory datasource directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ElementList, self).__init__(parent)
         ## directory from which components are loaded by default
        self.directory = directory
        
        ## group elements
        self.elements = {}

        ## actions
        self._actions = []

        ## user interface
        self.ui = Ui_ElementList()

        ## widget title
        self.title = "Elements"
        ## singular name
        self.clName = "Element"
        ## class name
        self.name = "elements"

    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.ui.setupUi(self)
        self.ui.elementTabWidget.setTabText(0, self.title)
        self.ui.elementListWidget.setEditTriggers(
            self.ui.elementListWidget.SelectedClicked)

        self.populateElements()




    ## opens context Menu        
    # \param position in the element list
    def _openMenu(self, position):
        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.ui.elementListWidget.viewport().mapToGlobal(position))


    ## sets context menu actions for the element list
    # \param actions tuple with actions 
    def setActions(self, actions):
        self.ui.elementListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.elementListWidget.customContextMenuRequested.connect(
            self._openMenu)
        self._actions = actions
        
            


    ## adds an element    
    #  \brief It runs the Element Dialog and fetches element 
    #         name and value    
    def addElement(self, obj, flag = True):
        self.elements[obj.id] = obj

        self.populateElements(obj.id, flag)
                
                
    ## takes a name of the current element
    # \returns name of the current element            
    def currentListElement(self):
        item = self.ui.elementListWidget.currentItem()
        if item is None:
            return None
        return self.elements[item.data(Qt.UserRole).toLongLong()[0]] 


    ## removes the current element    
    #  \brief It removes the current element asking before about it
    def removeElement(self, obj = None, question = True):
        
        if obj is not None:
            oid = obj.id
        else:    
            cds = self.currentListElement()
            if cds is None:
                return
            oid = cds.id
        if oid is None:
            return
        if oid in self.elements.keys():
            if question :
                if QMessageBox.question(
                    self, "%s - Close" % self.clName,
                    "Close %s: %s ".encode() \
                        %  (self.clName, self.elements[oid].name),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes ) == QMessageBox.No :
                    return

            self.elements.pop(oid)
            self.populateElements()
            



    ## changes the current value of the element        
    # \brief It changes the current value of the element and informs 
    #        the user that element names arenot editable
    def listItemChanged(self, item, name = None):
        ide =  self.currentListElement().id 
        if ide in self.elements.keys():
            old = self.elements[ide]
            oname = self.elements[ide].name
            if name is None:
                self.elements[ide].name = unicode(item.text())
            else:
                self.elements[ide].name = name
            self.populateElements()
            return old, oname


    ## fills in the element list      
    # \param selectedElement selected element    
    # \param edit flag if edit the selected item
    def populateElements(self, selectedElement = None, edit = False):
        selected = None
        self.ui.elementListWidget.clear()

        slist = [(self.elements[key].name, key) 
                 for key in self.elements.keys()]
        slist.sort()

        for name, el in slist:
            item = QListWidgetItem(QString("%s" % name))
            item.setData(Qt.UserRole, QVariant(self.elements[el].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            dirty = False
            if hasattr(self.elements[el],"isDirty") \
                    and self.elements[el].isDirty():
                dirty = True
            if self.elements[el].instance is not None:
                if hasattr(self.elements[el].instance,"isDirty") \
                        and self.elements[el].instance.isDirty():
                    dirty = True
            if dirty:
                item.setForeground(Qt.red) 
            else:
                item.setForeground(Qt.black)


            self.ui.elementListWidget.addItem(item)
            if selectedElement is not None \
                    and selectedElement == self.elements[el].id:
                selected = item


            if self.elements[el].instance is not None \
                    and self.elements[el].instance.dialog is not None:
                try:
                    if  dirty:
                        self.elements[el].instance.dialog.\
                            setWindowTitle("%s [%s]*" % (name, self.clName))
                    else:
                        self.elements[el].instance.dialog.\
                            setWindowTitle("%s [%s]" % (name, self.clName))
                except:
#                    print "C++", self.elements[el].name
                    self.elements[el].instance.dialog = None

        if selected is not None:
            selected.setSelected(True)
            self.ui.elementListWidget.setCurrentItem(selected)
            if edit:
                self.ui.elementListWidget.editItem(selected)


    ## sets the elements
    # \param elements dictionary with the elements, i.e. name:xml
    # \param externalActions dictionary with external actions
    # \param itemActions actions of the context menu
    # \param new logical variableset to True if element is not saved
    def setList(self, elements, externalActions = None, 
                itemActions = None, new = False):
        if not os.path.isdir(self.directory):
            try:
                if os.path.exists(os.path.join(os.getcwd(), self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(), self.name))
                else:
                    self.directory = os.getcwd() 
            except:
                return
            
        ide = None    
        for elname in elements.keys():
                
            name = self.dashName(elname)
            dlg = self.createElement(name)    
            try:
                if str(elements[elname]).strip():
                    dlg.set(elements[elname], new)    
                else:    
                    if hasattr(dlg, "createHeader"):
                        dlg.createHeader()
                    QMessageBox.warning(
                        self, "%s cannot be loaded" % self.clName,
                        "%s %s without content" % (self.clName, elname))
            except:
                QMessageBox.warning(
                    self, "%s cannot be loaded" % self.clName,
                    "%s %s cannot be loaded" % (self.clName, elname))

            if hasattr(dlg, "dataSourceName"):    
                dlg.dataSourceName = elname

            if hasattr(dlg, "addContextMenu"):    
                dlg.addContextMenu(itemActions)
                
            if hasattr(dlg,"connectExternalActions"):     
                actions = externalActions if externalActions else {}
                dlg.connectExternalActions(**actions)    

            el = LabeledObject(name, dlg)
            if new:
                el.savedName = ""

            ide = id(el)
            self.elements[ide] =  el
            if el.instance is not None:
                el.instance.id = el.id
                if new and hasattr(el.instance, "applied"):
                    el.instance.applied =  True
            print name
        return ide 



    ## replaces name special characters by underscore
    # \param name give name
    # \returns replaced element            
    @classmethod            
    def dashName(cls, name):
        return name 

            
    ## loads the element list from the given dictionary
    # \param externalActions dictionary with external actions
    # \param itemActions actions of the context menu
    def loadList(self, externalActions = None, itemActions=None):
        try:
            dirList = [l for l in  os.listdir(self.directory) \
                           if l.endswith(self.extention)]
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(), self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(), self.name))
                else:
                    self.directory = os.getcwd()

                dirList = [l for l in  os.listdir(self.directory) \
                               if l.endswith(self.extention)]
            except:
                return

        for fname in dirList:
            name = self.nameFromFile(fname)
            dlg = self.createElement(name)
            dlg.load()    
            if hasattr(dlg, "addContextMenu"):
                dlg.addContextMenu(itemActions)

            actions = externalActions if externalActions else {}
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(**actions)    
            
            el = LabeledObject(name, dlg)
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
    form = ElementList("../datasources")
#    form.elements={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.elements:
        print "Other datasources:"
        for k in form.elements.keys():
            print  " %s = '%s' " % (k, form.elements[k])
    
