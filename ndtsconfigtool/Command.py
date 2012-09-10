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
    def __init__(self,receiver, slot):
        self.receiver = receiver
        self._slot = slot


    def connectSlot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
        
    ## 
    def execute(self):
        pass
    ## 
    def unexecute(self):
        pass

    def clone(self): 
        pass

class ComponentNew(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._comp = None
        

    def execute(self):       
        if self._comp is None:
            self._comp = LabeledObject("", None)
        self.receiver.componentList.addComponent(self._comp)
        print "EXEC componentNew"

    def unexecute(self):
        if self._comp is not None:
            self.receiver.componentList.removeComponent(self._comp, False)

            if hasattr(self._comp,'widget') and \
                    self._comp.widget in self.receiver.mdi.windowList():
            
                self.receiver.mdi.setActiveWindow(self._comp.widget) 
                self.receiver.mdi.closeActiveWindow() 
            
        print "UNDO componentNew"

    def clone(self):
        return ComponentNew(self.receiver, self._slot) 





class ComponentOpen(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._cpEdit = None
        self._cp = None
        self._fpath = None
        
    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self._cp = LabeledObject("", None)
            self._cpEdit = ComponentDlg()
            self._cpEdit.idc = self._cp.id
            self._cpEdit.directory = self.receiver.componentList.directory
            self._cpEdit.createGUI()
            self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
            if self._fpath:
                path = self._cpEdit.load(self._fpath)
            else:
                path = self._cpEdit.load()
                self._fpath = path

            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(self.receiver.componentSave, 
                                                    self.receiver.componentApplyItem)    


            if path:   
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
            if self._fpath:
                self._cp.widget.setAttribute(Qt.WA_DeleteOnClose)



                if hasattr(self._cp,'widget') and \
                        self._cp.widget in self.receiver.mdi.windowList():
                    self.receiver.mdi.setActiveWindow(self._cp.widget) 
                    self.receiver.mdi.closeActiveWindow() 

                self.receiver.componentList.removeComponent(self._cp, False)
                self._cp.widget = None
                self._cp = None


            
        print "UNDO componentOpen"

    def clone(self):
        return ComponentOpen(self.receiver, self._slot) 




class DataSourceOpen(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._dsEdit = None
        self._ds = None
        self._fpath = None
        
    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self._ds = LabeledObject("", None)
            self._dsEdit = DataSourceDlg()
            self._dsEdit.ids = self._ds.id
            self._dsEdit.directory = self.receiver.sourceList.directory
            if self._fpath:
                path = self._dsEdit.load(self._fpath)
            else:
                path = self._dsEdit.load()
                self._fpath = path
            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(self.receiver.dsourceSave,
                                                    self.receiver.dsourceApply)    
            if path:   
                self._ds.name = self._dsEdit.name  
                self._ds.widget = self._dsEdit
            
                self.receiver.sourceList.addDataSource(self._ds,False)
            #               print  "ID", self._cp.id
 #               print "STAT", self._cp.id in self.receiver.componentList.components
                self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)                  

                if self._ds.widget in self.receiver.mdi.windowList():
                    self.receiver.mdi.setActiveWindow(self._ds.widget) 
                    self._ds.widget.savePushButton.setFocus()
                else:    
 #               print "create"
                    self.receiver.mdi.addWindow(self._dsEdit)
                    self._dsEdit.savePushButton.setFocus()
                    self._dsEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                    self._ds.widget = self._dsEdit 



                self.receiver.mdi.addWindow(self._dsEdit)
#            self._component.setAttribute(Qt.WA_DeleteOnClose)
                self._dsEdit.show()
                print "EXEC dsourceOpen"

    def unexecute(self):
        if hasattr(self._ds, "widget"):
            if self._fpath:
                self._ds.widget.setAttribute(Qt.WA_DeleteOnClose)


                if hasattr(self._ds,'widget') and \
                        self._ds.widget in self.receiver.mdi.windowList():

                    self.receiver.mdi.setActiveWindow(self._ds.widget) 
                    self.receiver.mdi.closeActiveWindow() 

                self.receiver.sourceList.removeDataSource(self._ds, False)
                self._ds.widget = None
                self._ds = None


            
        print "UNDO dsourceOpen"

    def clone(self):
        return DataSourceOpen(self.receiver, self._slot) 




class ComponentRemove(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._wList = False
        
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
        return ComponentRemove(self.receiver, self._slot) 


class ComponentEdit(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = ComponentDlg()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)
            else:
                self._cpEdit = self._cp.widget 
                
            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(self.receiver.componentSave, 
                                                    self.receiver.componentApplyItem)    



            if self._cp.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._cp.widget) 
            else:    
                self.receiver.mdi.addWindow(self._cpEdit)
                self._cpEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._cp.widget = self._cpEdit 
                    


            
        print "EXEC componentEdit"

    def unexecute(self):
        print "UNDO componentEdit"

    def clone(self):
        return ComponentEdit(self.receiver, self._slot) 




class ComponentClear(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):

        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if not self._cp:
            retrun    
        if QMessageBox.question(self.receiver, "Component - Clear",
                                "Clear the component: %s ".encode() %  (self._cp.name),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return

        if hasattr(self._cp,"widget") and self._cp.widget in self.receiver.mdi.windowList():
            self._wList = True
            self.receiver.mdi.setActiveWindow(self._cp.widget)
            self.receiver.mdi.closeActiveWindow()

        self._cpEdit = ComponentDlg()
        self._cpEdit.idc = self._cp.id
        self._cpEdit.directory = self.receiver.componentList.directory
        self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
        self._cpEdit.createGUI()
        self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
        self._cpEdit.createHeader()
        self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)
                

        if hasattr(self._cpEdit,"connectExternalActions"):     
            self._cpEdit.connectExternalActions(self.receiver.componentSave, 
                                                self.receiver.componentApplyItem)    


        if self._cp.widget in self.receiver.mdi.windowList():
            self.receiver.mdi.setActiveWindow(self._cp.widget) 
        else:    
            self.receiver.mdi.addWindow(self._cpEdit)
            self._cpEdit.show()
            self._cp.widget = self._cpEdit 
            
        print "EXEC componentClear"

    def unexecute(self):
        print "UNDO componentClear"

    def clone(self):
        return ComponentClear(self.receiver, self._slot) 


class ComponentSave(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = ComponentDlg()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)
            else:
                self._cpEdit = self._cp.widget 
                
            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(self.receiver.componentSave, 
                                                    self.receiver.componentApplyItem)    



            if self._cp.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._cp.widget) 
            else:    
                self.receiver.mdi.addWindow(self._cpEdit)
                self._cpEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._cp.widget = self._cpEdit 
                    
            self._cpEdit.save()    

            
        print "EXEC componentSave"

    def unexecute(self):
        print "UNDO componentSave"

    def clone(self):
        return ComponentSave(self.receiver, self._slot) 



class ComponentSaveAll(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    def execute(self):
            
        for icp in self.receiver.componentList.components.keys():
            cp = self.receiver.componentList.components[icp]
            if cp.widget is not None:
                cp.widget.save()    

        print "EXEC componentSaveAll"

    def unexecute(self):
        print "UNDO componentSaveAll"

    def clone(self):
        return ComponentSaveAll(self.receiver, self._slot) 



class ComponentSaveAs(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = ComponentDlg()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)
            else:
                self._cpEdit = self._cp.widget 
                

            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(self.receiver.componentSave, 
                                                    self.receiver.componentApplyItem)    


            if self._cp.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._cp.widget) 
            else:    
                self.receiver.mdi.addWindow(self._cpEdit)
                self._cpEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._cp.widget = self._cpEdit 
                    
            self._cpEdit.saveAs()    
#            self.receiver.loadComponents()

            
        print "EXEC componentSaveAs"

    def unexecute(self):
        print "UNDO componentSaveAs"

    def clone(self):
        return ComponentSaveAs(self.receiver, self._slot) 



class ComponentChangeDirectory(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    def execute(self):
        if QMessageBox.question(self.receiver, "Component - Change Directory",
                                "All unsaved components will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return


        path = unicode(QFileDialog.getExistingDirectory(
                self.receiver, "Open Directory",
                self.receiver.cpDirectory,
                QFileDialog.ShowDirsOnly or QFileDialog.DontResolveSymlinks))

        if not path:
            return
        dialogs = self.receiver.mdi.windowList()
        if dialogs:
            for dialog in dialogs:
                if isinstance(dialog,ComponentDlg):
                    self.receiver.mdi.setActiveWindow(dialog)
                    self.receiver.mdi.closeActiveWindow()



        self.receiver.componentList.components = {} 
        self.receiver.cpDirectory = path
        self.receiver.componentList.directory = path

        self.receiver.loadComponents()

        print "EXEC componentChangeDirectory"

    def unexecute(self):
        print "UNDO componentChangeDirectory"

    def clone(self):
        return ComponentChangeDirectory(self.receiver, self._slot) 


class DataSourceApply(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._dsEdit = None
        
        
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None:
            if self._ds.widget is None:
                self._dsEdit = DataSourceDlg()
                self._dsEdit.ids = self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
                self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._dsEdit.createGUI()
                self._dsEdit.createHeader()
                self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)
            else:
                self._dsEdit = self._ds.widget 

            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(self.receiver.dsourceSave, 
                                                    self.receiver.dsourceApply)    
    
            if self._ds.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._ds.widget) 
            else:    
                self.receiver.mdi.addWindow(self._dsEdit)
                self._dsEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._ds.widget = self._dsEdit 
                    
            self._dsEdit.apply()    

            
        print "EXEC dsourceApply"

    def unexecute(self):
        print "UNDO dsourceApply"

    def clone(self):
        return DataSourceApply(self.receiver, self._slot) 






class DataSourceSaveAll(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    def execute(self):
            
        for icp in self.receiver.sourceList.datasources.keys():
            cp = self.receiver.sourceList.datasources[icp]
            if cp.widget is not None:
                cp.widget.save()    

        print "EXEC dsourceSaveAll"

    def unexecute(self):
        print "UNDO dsourceSaveAll"

    def clone(self):
        return DataSourceSaveAll(self.receiver, self._slot) 


class DataSourceSave(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._dsEdit = None
        
        
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None:
            if self._ds.widget is None:
                self._dsEdit = DataSourceDlg()
                self._dsEdit.ids = self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
                self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._dsEdit.createGUI()
                self._dsEdit.createHeader()
                self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)
            else:
                self._dsEdit = self._ds.widget 

            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(self.receiver.dsourceSave,
                                                    self.receiver.dsourceApply)    
    
            if self._ds.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._ds.widget) 
            else:    
                self.receiver.mdi.addWindow(self._dsEdit)
                self._dsEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._ds.widget = self._dsEdit 
                    
            self._dsEdit.save()    

            
        print "EXEC dsourceSave"

    def unexecute(self):
        print "UNDO dsourceSave"

    def clone(self):
        return DataSourceSave(self.receiver, self._slot) 






class DataSourceSaveAs(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._dsEdit = None
        
        
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None:
            if self._ds.widget is None:
                self._dsEdit = DataSourceDlg()
                self._dsEdit.ids = self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
                self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._dsEdit.createGUI()
                self._dsEdit.createHeader()
                self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)
            else:
                self._dsEdit = self._ds.widget 
                
            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(self.receiver.dsourceSave,
                                                    self.receiver.dsourceApply)    

            if self._ds.widget in self.receiver.mdi.windowList():
                self.receiver.mdi.setActiveWindow(self._ds.widget) 
            else:    
                self.receiver.mdi.addWindow(self._dsEdit)
                self._dsEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
                self._ds.widget = self._dsEdit 
                    
            self._dsEdit.saveAs()    

            
        print "EXEC dsourceSaveAs"

    def unexecute(self):
        print "UNDO dsourceSaveAs"

    def clone(self):
        return DataSourceSaveAs(self.receiver, self._slot) 




class DataSourceChangeDirectory(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    def execute(self):
        if QMessageBox.question(self.receiver, "DataSource - Change Directory",
                                "All unsaved datasources will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return


        path = unicode(QFileDialog.getExistingDirectory(
                self.receiver, "Open Directory",
                self.receiver.dsDirectory,
                QFileDialog.ShowDirsOnly or QFileDialog.DontResolveSymlinks))

        if not path:
            return
        dialogs = self.receiver.mdi.windowList()
        if dialogs:
            for dialog in dialogs:
                if isinstance(dialog,DataSourceDlg):
                    self.receiver.mdi.setActiveWindow(dialog)
                    self.receiver.mdi.closeActiveWindow()



        self.receiver.sourceList.datasources = {} 
        self.receiver.dsDirectory = path
        self.receiver.sourceList.directory = path

        self.receiver.loadDataSources()

        print "EXEC dsourceChangeDirectory"

    def unexecute(self):
        print "UNDO dsourceChangeDirectory"

    def clone(self):
        return DataSourceChangeDirectory(self.receiver, self._slot) 




class ComponentReloadList(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    def execute(self):
        if QMessageBox.question(self.receiver, "Component - Reload List",
                                "All unsaved components will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return

        
        dialogs = self.receiver.mdi.windowList()
        if dialogs:
            for dialog in dialogs:
                if isinstance(dialog,ComponentDlg):
                    self.receiver.mdi.setActiveWindow(dialog)
                    self.receiver.mdi.closeActiveWindow()

        self.receiver.componentList.components = {} 
        self.receiver.loadComponents()

        print "EXEC componentReloadList"

    def unexecute(self):
        print "UNDO componentReloadList"

    def clone(self):
        return ComponentReloadList(self.receiver, self._slot) 





class DataSourceReloadList(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    def execute(self):
        if QMessageBox.question(self.receiver, "DataSource - Reload List",
                                "All unsaved datasources will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return


        dialogs = self.receiver.mdi.windowList()
        if dialogs:
            for dialog in dialogs:
                if isinstance(dialog,DataSourceDlg):
                    self.receiver.mdi.setActiveWindow(dialog)
                    self.receiver.mdi.closeActiveWindow()

        self.receiver.sourceList.datasources = {} 
        self.receiver.loadDataSources()

        print "EXEC componentReloadList"

    def unexecute(self):
        print "UNDO componentReloadList"

    def clone(self):
        return DataSourceReloadList(self.receiver, self._slot) 



class ComponentRemoveItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver,slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is not None:
                if hasattr(self._cp.widget,"removeSelectedItem"):
                    self._cp.widget.removeSelectedItem()

            
        print "EXEC componentRemoveItem"

    def unexecute(self):
        print "UNDO componentRemoveItem"

    def clone(self):
        return ComponentRemoveItem(self.receiver, self._slot) 




class ComponentLoadComponentItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        self.itemName = ""
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is not None and self._cp.widget.view and  self._cp.widget.model:
                if hasattr(self._cp.widget,"loadComponentItem"):
                    self._cp.widget.loadComponentItem(self.itemName)

            
        print "EXEC componentLoadcomponentItem"

    def unexecute(self):
        print "UNDO componentLoadComponentItem"

    def clone(self):
        return ComponentLoadComponentItem(self.receiver, self._slot) 





class ComponentLoadDataSourceItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        self.itemName = ""
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is not None and self._cp.widget.view and  self._cp.widget.model:
                if hasattr(self._cp.widget,"loadDataSourceItem"):
                    self._cp.widget.loadDataSourceItem(self.itemName)

            
        print "EXEC componentLoadDataSourceItem"

    def unexecute(self):
        print "UNDO componentLoadDataSourceItem"

    def clone(self):
        return ComponentLoadDataSourceItem(self.receiver, self._slot) 




class ComponentAddDataSourceItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._ds = None
        self._dsEdit = None
        self._cpEdit = None
        self._dsNode = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
            if self._cp is None:
                return
        if self._cp.widget is None or self._cp.widget.view is None or self._cp.widget.model is None:
            return

        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
            if self._ds is None:
                return

        if self._ds.widget is None:
            #                self._dsEdit = FieldWg()  
            self._dsEdit = DataSourceDlg()
            self._dsEdit.ids = self._ds.id
            self._dsEdit.directory = self.receiver.sourceList.directory
            self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
            self._dsEdit.createGUI()
            self._dsEdit.setWindowTitle("DataSource: %s" % self._ds.name)
            self._ds.widget = self._dsEdit 
        else:
            self._dsEdit = self._ds.widget 

        if hasattr(self._dsEdit,"connectExternalActions"):     
            self._dsEdit.connectExternalActions(self.receiver.dsourceSave,
                                                self.receiver.dsourceApply)    
                
        if not hasattr(self._ds.widget,"createNodes"):
            return

        self._dsNode = self._ds.widget.createNodes()
        if self._dsNode is None:
            return
        
        if not hasattr(self._cp.widget,"addDataSourceItem"):
            return
        self._cp.widget.addDataSourceItem(self._dsNode)

            
        print "EXEC componentAddDataSourceItem"

    def unexecute(self):
        print "UNDO componentAddDataSourceItem"

    def clone(self):
        return ComponentAddDataSourceItem(self.receiver, self._slot) 



class ComponentApplyItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is not None:
                if hasattr(self._cp.widget,"applyItem"):
                    self._cp.widget.applyItem()

            
        print "EXEC componentApplyItem"

    def unexecute(self):
        print "UNDO componentApplyItem"

    def clone(self):
        return ComponentApplyItem(self.receiver, self._slot) 



class ComponentNewItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        self.itemName = ""
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.widget is not None:
                if hasattr(self._cp.widget,"addItem"):
                    self._cp.widget.addItem(self.itemName)

            
        print "EXEC componentNewItem"

    def unexecute(self):
        print "UNDO componentNewItem"

    def clone(self):
        return ComponentNewItem(self.receiver, self._slot) 





class ComponentMerge(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is  None:
            return
        if self._cp.widget is None:
            #                self._cpEdit = FieldWg()  
            self._cpEdit = ComponentDlg()
            self._cpEdit.idc = self._cp.id
            self._cpEdit.directory = self.receiver.componentList.directory
            self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
            self._cpEdit.createGUI()
            self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
            self._cpEdit.createHeader()
            self._cpEdit.setWindowTitle("Component: %s" % self._cp.name)
        else:
            self._cpEdit = self._cp.widget 

        if hasattr(self._cpEdit,"connectExternalActions"):     
            self._cpEdit.connectExternalActions(self.receiver.componentSave, 
                                                self.receiver.componentApplyItem)    


                
        if self._cp.widget in self.receiver.mdi.windowList():
            self.receiver.mdi.setActiveWindow(self._cp.widget) 
        else:    
            self.receiver.mdi.addWindow(self._cpEdit)
            self._cpEdit.show()
                #                self._cpEdit.setAttribute(Qt.WA_DeleteOnClose)
            self._cp.widget = self._cpEdit 
                    
        if hasattr(self._cp.widget,"merge"):
            self._cp.widget.merge()


            
        print "EXEC componentMerge"

    def unexecute(self):
        print "UNDO componentMerge"

    def clone(self):
        return ComponentMerge(self.receiver, self._slot) 





class ComponentListChanged(Command):
    def __init__(self, receiver,slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self.item = None
        self.name = None
        self.newName = None
        
    def execute(self):
        if self.item is not None:
            if self.newName is None:
                self.newName = unicode(self.item.text())
            if self._cp is None:
                self._cp, self.name = self.receiver.componentList.listItemChanged(self.item)
            else:
                self._cp.name = self.newName
            
            self.receiver.componentList.populateComponents(self._cp.id)
            if self._cp.widget is not None:
                self._cp.widget.name = self.newName
        print "EXEC componentChanged"

    def unexecute(self):
        if self._cp is not None:
            self._cp.name = self.name 
            self.receiver.componentList.addComponent(self._cp, False)
        print "UNDO componentChanged"

    def clone(self):
        return ComponentListChanged(self.receiver, self._slot) 
    


class DataSourceNew(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        
    def execute(self):
        
        if self._ds is None:
            self._ds = LabeledObject("", None)
            
        self.receiver.sourceList.addDataSource(self._ds)
        print "EXEC dsourceNew"

    def unexecute(self):
        if self._ds is not None:
            self.receiver.sourceList.removeDataSource(self._ds, False)


            if hasattr(self._ds,'widget') and \
                    self._ds.widget in self.receiver.mdi.windowList():

                self.receiver.mdi.setActiveWindow(self._ds.widget) 
                self.receiver.mdi.closeActiveWindow() 

        print "UNDO dsourceNew"

    def clone(self):
        return DataSourceNew(self.receiver, self._slot) 






class DataSourceEdit(Command):
    def __init__(self, receiver,slot):
        Command.__init__(self, receiver,slot)
        self._ds = None
        self._dsEdit = None
        
        
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
                
            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(self.receiver.dsourceSave,
                                                    self.receiver.dsourceApply)    

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
        return DataSourceEdit(self.receiver, self._slot) 







class DataSourceRemove(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._wList = False
        
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
        return DataSourceRemove(self.receiver, self._slot) 



class DataSourceListChanged(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self.item = None
        self.name = None
        self.newName = None
        
    def execute(self):
        if self.item is not None:
            if self.newName is None:
                self.newName = unicode(self.item.text())
            if self._ds is None:
                self._ds, self.name = self.receiver.sourceList.listItemChanged(self.item)
            else:
                self._ds.name = self.newName

            self.receiver.sourceList.populateDataSources(self._ds.id)
            if self._ds.widget is not None:
                self._ds.widget.name = self.newName
        print "EXEC dsourceChanged"

    def unexecute(self):
        if self._ds is not None:
            self._ds.name = self.name 
            self.receiver.sourceList.addDataSource(self._ds, False)
        print "UNDO dsourceChanged"

    def clone(self):
        return DataSourceListChanged(self.receiver, self._slot) 
    




class CloseApplication(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self.receiver.close()
            print "EXEC closeApp"

    def unexecute(self):
        print "UNDO closeApp"

    def clone(self):
        return CloseApplication(self.receiver, self._slot) 



class UndoCommand(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    def execute(self):
        print "EXEC undo"

    def unexecute(self):
        pass

    def clone(self):
        return UndoCommand(self.receiver, self._slot) 

class ReundoCommand(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    def execute(self):
        print "EXEC reundo"

    def unexecute(self):
        pass

    def clone(self):
        return ReundoCommand(self.receiver, self._slot) 


        

if __name__ == "__main__":
    import sys

    pool = []
