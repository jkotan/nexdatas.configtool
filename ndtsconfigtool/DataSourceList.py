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
## \file DataSourceList.py
# Data source list class

import re
from PyQt4.QtCore import (SIGNAL, Qt, QString, QVariant)
from PyQt4.QtGui import (QWidget, QMenu, QMessageBox, QListWidgetItem)
from ui.ui_datasourcelist import  Ui_DataSourceList
from DataSourceDlg import DataSource
import os 


from LabeledObject import LabeledObject


## dialog defining a group tag
class DataSourceList(QWidget):
    
    ## constructor
    # \param directory datasource directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(DataSourceList, self).__init__(parent)
         ## directory from which components are loaded by default
        self.directory = directory
        
        ## group datasources
        self.datasources = {}

        ## actions
        self._actions = []

        ## user interface
        self.ui = Ui_DataSourceList()

    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.ui.setupUi(self)
        self.ui.sourceListWidget.setEditTriggers(self.ui.sourceListWidget.SelectedClicked)

        self.populateDataSources()




    ## opens context Menu        
    # \param position in the datasource list
    def _openMenu(self, position):
        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.ui.sourceListWidget.viewport().mapToGlobal(position))


    ## sets context menu actions for the datasource list
    # \param actions tuple with actions 
    def setActions(self, actions):
        self.ui.sourceListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.sourceListWidget.customContextMenuRequested.connect(self._openMenu)
        self._actions = actions
        
            

    ## loads the datasource list from the given dictionary
    # \param externalSave save action
    # \param externalApply apply action
    # \param externalClose close action
    def loadList(self, externalSave = None, externalApply = None , externalClose = None ):
        try:
            dirList=[l for l in  os.listdir(self.directory) if l.endswith(".ds.xml")]
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(),"datasources")):
                    self.directory = os.path.abspath(os.path.join(os.getcwd(),"datasources"))
                else:
                    self.directory = os.getcwd()

                dirList=[l for l in  os.listdir(self.directory) if l.endswith(".ds.xml")]
            except:
                return

        for fname in dirList:
            if fname[-4:] == '.xml':
                name = fname[:-4]
                if name[-3:] == '.ds':
                    name = name[:-3]
            else:
                name = fname
                
            dlg = DataSource()
            dlg.directory = self.directory
            dlg.name = name
            dlg.load()    

            
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(externalApply, externalSave, externalClose)    
            
            ds = LabeledObject(name, dlg)
            self.datasources[id(ds)] =  ds
            if ds.instance is not None:
                ds.instance.ids = ds.id
            print name



    ## sets the datasources
    # \param datasources dictionary with the datasources, i.e. name:xml
    # \param externalSave save action
    # \param externalApply apply action
    # \param externalClose close action
    # \param new logical variableset to True if datasource is not saved
    def setList(self, datasources, externalSave = None, externalApply = None, externalClose = None, new = False):
        try:
            dirList=os.listdir(self.directory)
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(),"datasources")):
                    self.directory = os.path.abspath(os.path.join(os.getcwd(),"datasources"))
                else:
                    self.directory = os.getcwd()
            except:
                return
            
        ids = None    
        for dsname in datasources.keys():

            name =  "".join(x.replace('/','_').replace('\\','_').replace(':','_') \
                                for x in dsname if (x.isalnum() or x in ["/","\\",":","_"]))
            dlg = DataSource()
            dlg.directory = self.directory
            dlg.name = name
            
            dlg.set(datasources[dsname], new)    

            dlg.dataSourceName = dsname

            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(externalApply, externalSave, externalClose)    
            
            ds = LabeledObject(name, dlg)
            if new:
                ds.savedName = ""

            ids = id(ds)
            self.datasources[ids] =  ds
            if ds.instance is not None:
                ds.instance.ids = ds.id
                if new:
                    ds.instance.applied =  True
            print name
        return ids    

    ## adds an datasource    
    #  \brief It runs the DataSource Dialog and fetches datasource name and value    
    def addDataSource(self, obj, flag = True):
        self.datasources[obj.id] = obj

        self.populateDataSources(obj.id, flag)
                
                
    ## takes a name of the current datasource
    # \returns name of the current datasource            
    def currentListDataSource(self):
        item = self.ui.sourceListWidget.currentItem()
        if item is None:
            return None
        return self.datasources[item.data(Qt.UserRole).toLongLong()[0]] 


    ## removes an datasource    
    #  \brief It removes the current datasource asking before about it
    def removeDataSource(self, obj = None, question = True):
        
        if obj is not None:
            oid = obj.id
        else:    
            cds = self.currentListDataSource()
            if cds is None:
                return
            oid = cds.id
        if oid is None:
            return
        if oid in self.datasources.keys():
            if question :
                if QMessageBox.question(self, "DataSource - Close",
                                        "Close datasource: %s ".encode() %  (self.datasources[oid].name),
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes ) == QMessageBox.No :
                    return

            self.datasources.pop(oid)
            self.populateDataSources()
            



    ## changes the current value of the datasource        
    # \brief It changes the current value of the datasource and informs the user that datasource names arenot editable
    def listItemChanged(self, item , name = None):
        ids =  self.currentListDataSource().id 
        if ids in self.datasources.keys():
            old = self.datasources[ids]
            oname = self.datasources[ids].name
            if name is None:
                self.datasources[ids].name = unicode(item.text())
            else:
                self.datasources[ids].name = name
            self.populateDataSources()
            return old, oname


    ## fills in the datasource list      
    # \param selectedDataSource selected datasource    
    # \param edit flag if edit the selected item
    def populateDataSources(self, selectedDataSource = None, edit = False):
        selected = None
        self.ui.sourceListWidget.clear()

        slist = [(self.datasources[key].name, key) 
                 for key in self.datasources.keys()]
        slist.sort()

        for name, ds in slist:
            item = QListWidgetItem(QString("%s" % name))
            item.setData(Qt.UserRole, QVariant(self.datasources[ds].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            dirty = False
            if hasattr(self.datasources[ds],"isDirty") \
                    and self.datasources[ds].isDirty():
                dirty = True
            if self.datasources[ds].instance is not None:
                if hasattr(self.datasources[ds].instance,"isDirty") \
                        and self.datasources[ds].instance.isDirty():
                    dirty = True
            if dirty:
                item.setForeground(Qt.red) 
            else:
                item.setForeground(Qt.black)


            self.ui.sourceListWidget.addItem(item)
            if selectedDataSource is not None and selectedDataSource == self.datasources[ds].id:
                selected = item


            if self.datasources[ds].instance is not None and self.datasources[ds].instance.dialog is not None:
                try:
                    if  dirty:
                        self.datasources[ds].instance.dialog.setWindowTitle("DataSource: %s*" %name)
                    else:
                        self.datasources[ds].instance.dialog.setWindowTitle("DataSource: %s" %name)
                except:
#                    print "C++", self.datasources[ds].name
                    self.datasources[ds].instance.dialog = None

        if selected is not None:
            selected.setSelected(True)
            self.ui.sourceListWidget.setCurrentItem(selected)
            if edit:
                self.ui.sourceListWidget.editItem(selected)

            



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
    form = DataSourceList("../datasources")
#    form.datasources={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.datasources:
        print "Other datasources:"
        for k in form.datasources.keys():
            print  " %s = '%s' " % (k, form.datasources[k])
    
