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
## \file Command.py
# user commands of GUI application

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from DataSourceList import DataSourceList
from DataSourceDlg import DataSourceDlg
#from FieldWg import FieldWg

from ComponentList import ComponentList
from ComponentDlg import ComponentDlg
from LabeledObject import LabeledObject

## abstract command
class Command(object):
    
    ## constructor
    def __init__(self):
        pass

    ## 
    def execute(self):
        pass
    ## 
    def unexecute(self):
        pass

    def clone(self): 
        pass

class ComponentNew(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'componentNew'
        self._comp = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):       
        if self._comp is None:
            self._comp = LabeledObject("", None)
        self.receiver.componentList.addComponent(self._comp)

    def unexecute(self):
        if self._comp is not None:
            self.receiver.componentList.removeComponent(self._comp, False)

        print "UNDO componentNew"

    def clone(self):
        return ComponentNew(self.receiver) 





class ComponentOpen(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'componentOpen'
        self._cpEdit = None
        self._cp = None
        self._fpath = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self._cp = LabeledObject("", None)
            self._cpEdit = ComponentDlg()
            self._cpEdit.idc = self._cp.id
            self._cpEdit.directory = self.receiver.componentList.directory
            self._cpEdit.createGUI()
            if self._fpath:
                self._cpEdit.load(self._fpath)
            else:
                self._fpath = self._cpEdit.load()
            self._cp.name = self._cpEdit.name  
            self._cp.widget = self._cpEdit
            
            self.receiver.componentList.addComponent(self._cp,False)
            #               print  "ID", self._cp.id
 #               print "STAT", self._cp.id in self.receiver.componentList.components
            self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)                  

            if self._cp.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._cp.widget) 
                self._cp.widget.savePushButton.setFocus()
            else:    
 #               print "create"
                self.receiver.mdi.addWindow(self._cpEdit)
                self._cpEdit.savePushButton.setFocus()
                self._cpEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._cp.widget = self._cpEdit 



            self.receiver.mdi.addWindow(self._cpEdit)
#            self._component.setAttribute(Qt.WA_DeleteOnClose)
            self._cpEdit.show()
            print "EXEC componentOpen"

    def unexecute(self):
        if hasattr(self._cp, "widget"):
            self._cp.widget.setAttribute(Qt.WA_DeleteOnClose)

            self.receiver.mdi.setActiveWindow(self._cp.widget) 
            self.receiver.mdi.closeActiveWindow() 

            self.receiver.componentList.removeComponent(self._cp, False)
            self._cp.widget = None
            self._cp = None


            
        print "UNDO componentOpen"

    def clone(self):
        return ComponentOpen(self.receiver) 




class ComponentClicked(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'componentClicked'
        self._component = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        print "EXEC componentClicked"

    def unexecute(self):
        print "UNDO componentClicked"

    def clone(self):
        return ComponentClicked(self.receiver) 


class ComponentCurrentItemChanged(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'componentCurrentItemChanged'
        self._cp = None
        self._cpEdit = None
        self.item = None
        self.previousItem = None
        self._wasInWS = None
        self._wasCreated = None
        self._prevActive = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
#        print "IC: ", (self.item.text() if self.item else None),  (self.previousItem.text() if self.previousItem else None)

        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            self._prevActive = self.receiver.mdi.activeWindow()
            if self._cp.widget is None or self._wasCreated:
                #                self._cpEdit = FieldWg()  
                if self._wasCreated is None:
                    self._wasCreated  = True
                self._cpEdit = ComponentDlg() 
                self._cpEdit.idc = self._cp.id
 #               print  "ID", self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
 #               print "STAT", self._cp.id in self.receiver.componentList.components
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)  
            else:
                self._cpEdit = self._cp.widget 
#                print  "ID-e", self._cp.id
            if self._cp.widget in self.receiver.mdi.windowList() or self._wasInWS:
 #               print "show"
                if self._wasInWS is None : 
                    self._wasInWS = True
                self.receiver.mdi.setActiveWindow(self._cp.widget) 
                self._cp.widget.savePushButton.setFocus()
            else:    
 #               print "create"
                self.receiver.mdi.addWindow(self._cpEdit)
                self._cpEdit.savePushButton.setFocus()
                self._cpEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._cp.widget = self._cpEdit 
        if self._wasInWS is None : 
            self._wasInWS = False
        if self._wasCreated is None:
            self._wasCreated  = False

        print "EXEC componentCurrentItemChanged"

    def unexecute(self):
        if hasattr(self._cp, "widget"):
#            print  "ID-u", self._cp.id
            if self._wasCreated:
                self._cp.widget.setAttribute(Qt.WA_DeleteOnClose)
            if not self._wasInWS: 
#                print "close"
                self.receiver.mdi.setActiveWindow(self._cp.widget) 
                self.receiver.mdi.closeActiveWindow() 

            if self._wasCreated:
                self._cp.widget = None

            if self._prevActive:
#                print "prev"
                self.receiver.mdi.setActiveWindow(self._prevActive) 
                
                print "UNDO componentCurrentItemChanged"
        
    def clone(self):
        return ComponentCurrentItemChanged(self.receiver) 
    




class ComponentRemove(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'componentRemove'
        self._cp = None
        self._wList = False
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)

    def execute(self):
        
        if self._cp is not None:
            self.receiver.componentList.removeComponent(self._cp, False)
        else:
            self._cp = self.receiver.componentList.currentListComponent()
            if self._cp is not None:
                self.receiver.componentList.removeComponent(self._cp, True)
            
        ## TODO check     
        if hasattr(self._cp,"widget") and self._cp.widget in self.receiver.mdi.windowList():
            self._wList = True
            self.receiver.mdi.setActiveWindow(self._cp.widget)
            self.receiver.mdi.closeActiveWindow()
            
            

        print "EXEC componentRemove"

    def unexecute(self):
        if self._cp is not None:

            self.receiver.componentList.addComponent(self._cp, False)
        print "UNDO componentRemove"

    def clone(self):
        return ComponentRemove(self.receiver) 






class ComponentListChanged(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'componentChanged'
        self._ds = None
        self.item = None
        self.name = None
        self.newName = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
#        print "componentChange"
        if self.item is not None:
#            print "self.item is not None:"
            if self.newName is None:
#                print "self.newName is None:"
                self.newName = unicode(self.item.text())
            if self._ds is None:
#                print "self._ds is None:    "
                self._ds, self.name = self.receiver.componentList.listItemChanged(self.item)
            else:
#                print "not self._ds is None:    "
#                print "Name:", self.newName
                self._ds.name = self.newName
                self.receiver.componentList.populateComponents()
            if self._ds.widget is not None:
                self._ds.widget.name = self.newName
        print "EXEC componentChanged"

    def unexecute(self):
        if self._ds is not None:
            self._ds.name = self.name 
            self.receiver.componentList.addComponent(self._ds, False)
        print "UNDO componentChanged"

    def clone(self):
        return ComponentListChanged(self.receiver) 
    


class DataSourceNew(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceNew'
        self._ds = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        
        if self._ds is None:
            self._ds = LabeledObject("", None)
            
        self.receiver.sourceList.addDataSource(self._ds)
        print "EXEC dsourceNew"

    def unexecute(self):
        if self._ds is not None:
            self.receiver.sourceList.removeDataSource(self._ds, False)
        print "UNDO dsourceNew"

    def clone(self):
        return DataSourceNew(self.receiver) 






class DataSourceEdit(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceEdit'
        self._ds = None
        self._dsEdit = None
        
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None:
            if self._ds.widget is None:
                #                self._dsEdit = FieldWg()  
                self._dsEdit = DataSourceDlg()
                self._dsEdit.ids = self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
                self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._dsEdit.createGUI()
                self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)
            else:
                self._dsEdit = self._ds.widget 
                
            if self._ds.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._ds.widget) 
            else:    
                self.receiver.mdi.addWindow(self._dsEdit)
                self._dsEdit.show()
                #                self._dsEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._ds.widget = self._dsEdit 
                    


            
        print "EXEC dsourceEdit"

    def unexecute(self):
        print "UNDO dsourceEdit"

    def clone(self):
        return DataSourceEdit(self.receiver) 



class DataSourceNew(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceNew'
        self._ds = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        
        if self._ds is None:
            self._ds = LabeledObject("", None)
            
        self.receiver.sourceList.addDataSource(self._ds)
        print "EXEC dsourceNew"

    def unexecute(self):
        if self._ds is not None:
            self.receiver.sourceList.removeDataSource(self._ds, False)
        print "UNDO dsourceNew"

    def clone(self):
        return DataSourceNew(self.receiver) 








class DataSourceRemove(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceRemove'
        self._ds = None
        self._wList = False
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)

    def execute(self):
        
        if self._ds is not None:
            self.receiver.sourceList.removeDataSource(self._ds, False)
        else:
            self._ds = self.receiver.sourceList.currentListDataSource()
            if self._ds is not None:
                self.receiver.sourceList.removeDataSource(self._ds, True)
            
        ## TODO check     
        if hasattr(self._ds,"widget") and self._ds.widget in self.receiver.mdi.windowList():
            self._wList = True
            self.receiver.mdi.setActiveWindow(self._ds.widget)
            self.receiver.mdi.closeActiveWindow()
            
            

        print "EXEC dsourceRemove"

    def unexecute(self):
        if self._ds is not None:

            self.receiver.sourceList.addDataSource(self._ds, False)
        print "UNDO dsourceRemove"

    def clone(self):
        return DataSourceRemove(self.receiver) 



class DataSourceListChanged(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceChanged'
        self._ds = None
        self.item = None
        self.name = None
        self.newName = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
#        print "dsourceChange"
        if self.item is not None:
#            print "self.item is not None:"
            if self.newName is None:
#                print "self.newName is None:"
                self.newName = unicode(self.item.text())
            if self._ds is None:
#                print "self._ds is None:    "
                self._ds, self.name = self.receiver.sourceList.listItemChanged(self.item)
            else:
#                print "not self._ds is None:    "
#                print "Name:", self.newName
                self._ds.name = self.newName
                self.receiver.sourceList.populateDataSources()
            if self._ds.widget is not None:
                self._ds.widget.name = self.newName
        print "EXEC dsourceChanged"

    def unexecute(self):
        if self._ds is not None:
            self._ds.name = self.name 
            self.receiver.sourceList.addDataSource(self._ds, False)
        print "UNDO dsourceChanged"

    def clone(self):
        return DataSourceListChanged(self.receiver) 
    






class DataSourceCurrentItemChanged(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceCurrentItemChanged'
        self._ds = None
        self._dsEdit = None
        self.item = None
        self.previousItem = None
        self._wasInWS = None
        self._wasCreated = None
        self._prevActive = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
#        print "IC: ", (self.item.text() if self.item else None),  (self.previousItem.text() if self.previousItem else None)

        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None:
            self._prevActive = self.receiver.mdi.activeWindow()
            if self._ds.widget is None or self._wasCreated:
                #                self._dsEdit = FieldWg()  
                if self._wasCreated is None:
                    self._wasCreated  = True
                self._dsEdit = DataSourceDlg() 
                self._dsEdit.ids = self._ds.id
 #               print  "ID", self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
 #               print "STAT", self._ds.id in self.receiver.sourceList.datasources
                self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._dsEdit.createGUI()
                self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)  
            else:
                self._dsEdit = self._ds.widget 
#                print  "ID-e", self._ds.id
            if self._ds.widget in self.receiver.mdi.windowList() or self._wasInWS:
 #               print "show"
                if self._wasInWS is None : 
                    self._wasInWS = True
                self.receiver.mdi.setActiveWindow(self._ds.widget) 
                self._ds.widget.savePushButton.setFocus()
            else:    
 #               print "create"
                self.receiver.mdi.addWindow(self._dsEdit)
                self._dsEdit.savePushButton.setFocus()
                self._dsEdit.show()
                #                self._dsEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._ds.widget = self._dsEdit 
        if self._wasInWS is None : 
            self._wasInWS = False
        if self._wasCreated is None:
            self._wasCreated  = False

        print "EXEC dsourceCurrentItemChanged"

    def unexecute(self):
        if hasattr(self._ds, "widget"):
#            print  "ID-u", self._ds.id
            if self._wasCreated:
                self._ds.widget.setAttribute(Qt.WA_DeleteOnClose)
            if not self._wasInWS: 
#                print "close"
                self.receiver.mdi.setActiveWindow(self._ds.widget) 
                self.receiver.mdi.closeActiveWindow() 

            if self._wasCreated:
                self._ds.widget = None

            if self._prevActive:
#                print "prev"
                self.receiver.mdi.setActiveWindow(self._prevActive) 
                
                print "UNDO dsourceCurrentItemChanged"
        
    def clone(self):
        return DataSourceCurrentItemChanged(self.receiver) 
    




class CloseApplication(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'closeApp'

    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self.receiver.close()
            print "EXEC closeApp"

    def unexecute(self):
        print "UNDO closeApp"

    def clone(self):
        return CloseApplication(self.receiver) 



class UndoCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'undo'

    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        print "EXEC undo"

    def unexecute(self):
        pass

    def clone(self):
        return UndoCommand(self.receiver) 

class ReundoCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'reundo'

    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        print "EXEC reundo"

    def unexecute(self):
        pass

    def clone(self):
        return ReundoCommand(self.receiver) 


class SimpleCommand(Command):
    def __init__(self, receiver, action, undo=None):
        self.receiver = receiver
        self.action = action
        self.undo = undo
        
    def execute(self):
        if hasattr(self.receiver,self.action):
            obj = getattr(self.receiver, self.action)
            if callable(obj):
                obj()

    def unexecute(self):
        if hasattr(self.receiver,self.undo):
            obj = getattr(self.receiver, self.undo)
            if callable(obj):
                obj()

    def clone(self):
        return SimpleCommand(receiver, action, undo)


class TextCommand(Command):
    def __init__(self, receiver, action, originator=None, undo=None ):
        self.receiver = receiver
        self.action = action
        self.undo = undo
        self.originator = originator
        self._state = None
        
    def execute(self):
        if hasattr(self.originator,'createMemento'):
            self._state = self.originator.createMemento()
            
        if hasattr(self.receiver,self.action):
            obj = getattr(self.receiver, self.action)
            if callable(obj):
                obj()

    def unexecute(self):
        if hasattr(self.receiver,self.undo):
            obj = getattr(self.receiver, self.undo)
            if callable(obj):
                obj()
            if hasattr(self.originator,'setMemento'):
                self.originator.setMemento(self._state)

    def clone(self):
        return TextCommand(receiver, action, originator, undo)



class ActionClass(object):        
    def __init__(self):
        self.txt = []

    def myAction(self):
        self.txt.append("ACTION !!!")
        print "Action: ", self.txt

    def undo(self):
        self.txt.pop()
 #       print "Undo: ", self.txt


class TextMemento(object):
    def __init__(self, txt):
        self.txt = txt


class ActionMemClass(object):        
    def __init__(self):
        self.txt = "ROOT: "

    def createMemento(self):
        return TextMemento(self.txt) 
    
    def setMemento(self,memento):
        self.txt = memento.txt

    def myAction(self):
        self.txt += "ACTION !!!"
#        print "Action: ", self.txt

    def undo(self):
        pass


        

if __name__ == "__main__":
    import sys

    pool = []
    
    actionObj2 = ActionClass()
    actionObj = ActionMemClass()
    print actionObj.txt
    print actionObj2.txt

    print "EXEC"
    cmd = TextCommand(actionObj, 'myAction', actionObj, 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj.txt

    print "EXEC"
    cmd = SimpleCommand(actionObj2, 'myAction', 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj2.txt


    print "EXEC"
    cmd = TextCommand(actionObj, 'myAction', actionObj, 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj.txt

    print "EXEC"
    cmd = SimpleCommand(actionObj2, 'myAction', 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj2.txt


    while pool:

        print "UNEXEC"
        cmd = pool.pop()
        if cmd:
            cmd.unexecute()
            print actionObj.txt
            print actionObj2.txt
