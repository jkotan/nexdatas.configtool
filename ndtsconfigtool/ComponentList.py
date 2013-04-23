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

import re
from PyQt4.QtCore import (SIGNAL, Qt, QString, QVariant)
from PyQt4.QtGui import (QWidget, QMenu, QMessageBox, QListWidgetItem)
from ui.ui_componentlist import Ui_ComponentList
import os

from ComponentDlg import Component
from LabeledObject import LabeledObject


## dialog defining a group tag
class ComponentList(QWidget):
    
    ## constructor
    # \param directory component directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ComponentList, self).__init__(parent)

        ## directory from which components are loaded by default
        self.directory = directory
        
        ## group components
        self.components = {}

        ## actions
        self._actions = []
        
        ## show all attribures or only the type attribute
        self._allAttributes = False

        ## user interface
        self.ui = Ui_ComponentList()


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.ui.setupUi(self)


#        self.connect(self.ui.componentListWidget, 
#                     SIGNAL("itemChanged(QListWidgetItem*)"),
#                     self.listItemChanged)

        self.populateComponents()


    ## switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status = None):
        if status is None:
            return self._allAttributes
        self._allAttributes = True if status else False
        for k in self.components.keys():
            if hasattr(self.components[k], "instance") and self.components[k].instance:
                 self.components[k].instance.viewAttributes(self._allAttributes)
            

    ## opens context Menu        
    # \param position in the component list
    def _openMenu(self, position):
        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.ui.componentListWidget.viewport().mapToGlobal(position))


    ## sets context menu actions for the component list
    # \param actions tuple with actions 
    def setActions(self, actions):
        self.ui.componentListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.componentListWidget.customContextMenuRequested.connect(self._openMenu)
        self._actions = actions
        
        

    ## adds an component    
    #  \brief It runs the Component Dialog and fetches component name and value    
    def addComponent(self, obj, flag = True):

        self.components[obj.id] = obj
        self.populateComponents(obj.id, flag)
                
                
    ## takes a name of the current component
    # \returns name of the current component            
    def currentListComponent(self):
        item = self.ui.componentListWidget.currentItem()
        if item is None:
            return None    
        return self.components[item.data(Qt.UserRole).toLongLong()[0]] 


    ## removes the current component    
    #  \brief It removes the current component asking before about it
    def removeComponent(self,obj = None, question = True):
        if obj is not None:
            oid = obj.id
        else:
            comp = self.currentListComponent()
            if comp is None:
                return
            oid = comp.id
        if oid is None:
            return
        if oid in self.components.keys():
            if question :
                if QMessageBox.question(self, "Component - Close",
                                        "Close the component: %s ".encode() %  (self.components[oid].name),
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes ) == QMessageBox.No :
                    return

            self.components.pop(oid)
            self.populateComponents()

        attr = self.currentListComponent()
        if attr is None:
            return
        if QMessageBox.question(self, "Component - Remove",
                                "Remove component: %s = \'%s\'".encode() %  (attr, self.components[unicode(attr)]),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return
        if unicode(attr) in self.components.keys():
            self.components.pop(unicode(attr))
            self.populateComponents()


    ## changes the current value of the component        
    # \brief It changes the current value of the component and informs the user that component names arenot editable
    def listItemChanged(self, item, name = None):
        icp = self.currentListComponent().id

        if icp in self.components.keys():
            old = self.components[icp] 
            oname = self.components[icp].name
            if name is None:
                self.components[icp].name = unicode(item.text())
            else:
                self.components[icp].name = name
            self.populateComponents()
            return old, oname


    ## fills in the component table      
    # \param selectedComponent selected component    
    # \param edit flag if the component should be edited
    def populateComponents(self, selectedComponent = None, edit = False):
#        print "populate"
        selected = None
        self.ui.componentListWidget.clear()
        
        slist = [(self.components[key].name, key) 
                 for key in self.components.keys()]
        slist.sort()
        
        for name, cp in slist:
            item  = QListWidgetItem(QString("%s" % name))
            item.setData(Qt.UserRole, QVariant(self.components[cp].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            dirty = False
            if hasattr(self.components[cp],"isDirty") \
                    and self.components[cp].isDirty():
                dirty = True
            if self.components[cp].instance is not None:
                if hasattr(self.components[cp].instance,"isDirty") \
                        and self.components[cp].instance.isDirty():
                    dirty = True
            if dirty:
                item.setForeground(Qt.red) 
            else:
                item.setForeground(Qt.black)

            self.ui.componentListWidget.addItem(item)
            if selectedComponent is not None and selectedComponent == self.components[cp].id:
                selected = item
                               
            if self.components[cp].instance is not None and self.components[cp].instance.dialog is not None:
                try:
                    if dirty:
                        self.components[cp].instance.dialog.setWindowTitle("Component: %s*" %name)
                    else:
                        self.components[cp].instance.dialog.setWindowTitle("Component: %s" %name)
                except:
#                    print "C++", self.components[cp].name
                    # C++ dialog was deleted
                    self.components[cp].instance.dialog =  None
        if selected is not None:
            selected.setSelected(True)
            self.ui.componentListWidget.setCurrentItem(selected)
            if edit:
                self.ui.componentListWidget.editItem(selected)


            
    ## loads the component list from the given dictionary
    # \param itemActions actions of the context menu
    # \param externalSave save action
    # \param externalApply apply action
    # \param externalClose close action
    # \param externalDSLink datasource link action
    def loadList(self, itemActions, externalSave = None, externalApply = None, 
                 externalClose = None, externalDSLink = None ):
        try:
            dirList=[l for l in os.listdir(self.directory) if l.endswith(".xml")]
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(),"components")):
                    self.directory = os.path.abspath(os.path.join(os.getcwd(),"components"))
                else:
                    self.directory = os.getcwd()
                dirList=[l for l in os.listdir(self.directory) if l.endswith(".xml")]
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
                dlg.connectExternalActions(externalApply, externalSave, externalClose, externalDSLink)    

            cp = LabeledObject(name, dlg)
            self.components[id(cp)] =  cp
            if cp.instance is not None:
                cp.instance.idc = cp.id
            print name
            


    ## sets the component
    # \param components dictionary with the components, i.e. name:xml
    # \param itemActions actions of the tree context menu
    # \param externalSave save action
    # \param externalApply apply action
    # \param externalClose close action
    # \param externalDSLink datasource link action
    def setList(self, components,  itemActions, externalSave = None, externalApply = None, 
                externalClose = None, externalDSLink = None ):
        try:
            dirList=os.listdir(self.directory)
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(),"components")):
                    self.directory = os.path.abspath(os.path.join(os.getcwd(),"components"))
                else:
                    self.directory = os.getcwd() 
            except:
                ## todo
                return
            
        for name in components.keys():
                
            dlg = Component()
            dlg.directory = self.directory
            dlg.name = name
            dlg.createGUI()
            dlg.addContextMenu(itemActions)

            dlg.set(components[name])    
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(externalApply, externalSave, externalClose, externalDSLink)    

            cp = LabeledObject(name, dlg)
            self.components[id(cp)] =  cp
            if cp.instance is not None:
                cp.instance.idc = cp.id
            print name
            





    ## accepts input text strings
    # \brief It copies the group name and type from lineEdit widgets and accept the dialog
    def accept(self):
        
        QWidget.accept(self)

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


    if form.components:
        print "Other components:"
        for k in form.components.keys():
            print  " %s = '%s' " % (k, form.components[k])
    
