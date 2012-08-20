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
## \file DataSourceList.py
# Data source list class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_datasourcelist
from DataSourceDlg import DataSourceDlg
import os 

class LabeledObject(object):
    def __init__(self, name , instance):
        self.name = name
        self.instance = instance
        self.id = id(self)


## dialog defining a group tag
class DataSourceList(QWidget, ui_datasourcelist.Ui_DataSourceList):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(DataSourceList, self).__init__(parent)
        self.directory = directory
        
        ## group datasources
        self.datasources = {}

    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.setupUi(self)



#        self.connect(self.sourceListWidget, 
#                     SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"),
#                     self.dsourceEdit)


        self.populateDataSources()

            

    def loadList(self):
        dirList=os.listdir(self.directory)
        for fname in dirList:
            if fname[-4:] == '.xml':
                name = fname[:-4]
                if name[-3:] == '.ds':
                    name = name[:-3]
            else:
                name = fname
                
            dlg = DataSourceDlg()
            dlg.directory = self.directory
            dlg.name = name
            dlg.load()    
            ds = LabeledObject(name, dlg)
            self.datasources[id(ds)] =  ds
            if ds.instance is not None:
                ds.instance.ids = ds.id
            print name

    ## adds an datasource    
    #  \brief It runs the DataSource Dialog and fetches datasource name and value    
    def addDataSource(self, obj, flag = True):
        self.datasources[obj.id] = obj

        self.populateDataSources(obj.id, flag)
                
                
    ## takes a name of the current datasource
    # \returns name of the current datasource            
    def currentListDataSource(self):
        item = self.sourceListWidget.currentItem()
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
                if QMessageBox.question(self, "DataSource - Remove",
                                        "Remove datasource: %s ".encode() %  (self.datasources[oid].name),
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
                    return

            self.datasources.pop(oid)
            self.populateDataSources()
            



    ## changes the current value of the datasource        
    # \brief It changes the current value of the datasource and informs the user that datasource names arenot editable
    def listItemChanged(self, item):
        ids =  self.currentListDataSource().id 
        if ids in self.datasources.keys():
            old = self.datasources[ids]
            oname = self.datasources[ids].name
            self.datasources[ids].name = unicode(item.text())
            self.populateDataSources()
            return old, oname

    ## fills in the datasource list      
    # \param selectedDataSource selected datasource    
    def populateDataSources(self, selectedDataSource = None, edit = False):
        selected = None
        self.sourceListWidget.clear()
        for ds in self.datasources.keys():
            name = self.datasources[ds].name
            item = QListWidgetItem(QString("%s" % name))
            item.setData(Qt.UserRole, QVariant(self.datasources[ds].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.sourceListWidget.addItem(item)
            if selectedDataSource is not None and selectedDataSource == self.datasources[ds].id:
                selected = item
            if self.datasources[ds].instance is not None:
                self.datasources[ds].instance.setWindowTitle("DataSource: %s" %name)

        if selected is not None:
            selected.setSelected(True)
            self.sourceListWidget.setCurrentItem(selected)
            if edit:
                self.sourceListWidget.editItem(selected)

            



    ## accepts input text strings
    # \brief It copies the group name and type from lineEdit widgets and accept the dialog
    def accept(self):
        
        QWidget.accept(self)

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = DataSourceList()
#    form.datasources={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.result():
        if form.datasources:
            print "Other datasources:"
            for k in form.datasources.keys():
                print  " %s = '%s' " % (k, form.datasources[k])
    
