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
## \file ComponentDlg.py
# component classes 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
                         QXmlInputSource, QXmlSimpleReader)
import ui_componentdlg
from FieldDlg import FieldDlg 
from GroupDlg import GroupDlg 
from LinkDlg import LinkDlg 
from RichAttributeDlg import RichAttributeDlg 
from DataSourceDlg import DataSourceDlg 
from DimensionsDlg import DimensionsDlg

import os

from ComponentModel import *    
from LabeledObject import LabeledObject

## dialog defining a tag link 
class ComponentDlg(QDialog,ui_componentdlg.Ui_ComponentDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(ComponentDlg, self).__init__(parent)

        self.xmlPath = os.path.dirname(".")
        self.view = None
        self.frame = None
        self.model = None
        
        ## component id
        self.idc = None
        self.name = ""


        self.tagClasses = {"field":FieldDlg, "group":GroupDlg, 
                           "attribute":RichAttributeDlg,"link":LinkDlg,
                           "datasource":DataSourceDlg,"dimensions":DimensionsDlg}
        self.widget = None

        self.currentTag = None
        self.frameLayout = None

    def setupForm(self):
        pass
        

    def createGUI(self):
        self.setupUi(self)


        self.model = ComponentModel(QDomDocument(),self)
        self.view.setModel(self.model)
        
        self.widget = QWidget()
#        self.widget.createGUI()

        self.frameLayout = QGridLayout()
        self.frameLayout.addWidget(self.widget)
        self.frame.setLayout(self.frameLayout)

        self.setupForm()

        
#       self.connect(self.applyPushButton, SIGNAL("clicked()"), 
#                     self.apply)
#        self.connect(self.savePushButton, SIGNAL("clicked()"), 
#                     self.save)
#        self.connect(self.cancelPushButton, SIGNAL("clicked()"), 
#                     self.cancel)


#        self.connect(self.dAddPushButton, SIGNAL("clicked()"), 
#                     self.addParameter)
#        self.connect(self.dRemovePushButton, SIGNAL("clicked()"), 
#                     self.removeParameter)
#        self.connect(self.dParameterTableWidget, 
#                     SIGNAL("itemChanged(QTableWidgetItem*)"),
#                     self.tableItemChanged)

        self.connect(self.view, 
                     SIGNAL("clicked(QModelIndex)"),
                     self.tagClicked)
        self.connect(self.view, 
                     SIGNAL("expanded(QModelIndex)"),
                     self.expanded)

        self.connect(self.view, 
                     SIGNAL("collapsed(QModelIndex)"),
                     self.collapsed)

#        self.pool.createTask("componentClicked",commandArgs, ComponentClicked,
#                             self.componentList.componentListWidget, 
#                             "clicked(QModelIndex)")


    def tagClicked(self, index):
        self.currentTag = index
        item  = self.currentTag.internalPointer()
        node = item.node
        attributeMap = node.attributes()
        nNode = node.nodeName()
        name = None
        if attributeMap.contains("name"):
            name = attributeMap.namedItem("name").nodeValue()

        print "Clicked:", nNode, ": "+ name if name else "" 


        self.widget.setVisible(False)
        if unicode(nNode) in self.tagClasses.keys():
            self.frame.hide()
            self.frameLayout.removeWidget(self.widget)
            self.widget = self.tagClasses[unicode(nNode)]()
            self.widget.createGUI()
            self.frameLayout.addWidget(self.widget)
            self.widget.show()
#            self.frameLayout.update()
            self.frame.show()
    
    def expanded(self,index):
        for column in range(self.model.columnCount(index)):
            self.view.resizeColumnToContents(column)

    def collapsed(self,index):
        for column in range(self.model.columnCount(index)):
            self.view.resizeColumnToContents(column)



    def load(self,filePath = None):
        
        if not filePath:
            if not self.name:
                fPath = unicode(QFileDialog.getOpenFileName(self,"Open File",self.xmlPath,
                                                            "XML files (*.xml);;HTML files (*.html);;"
                                                            "SVG files (*.svg);;User Interface files (*.ui)"))
            else:
                fPath = self.directory + "/" + self.name + ".xml"
        else:
            fPath = filePath
        if fPath:
            try:
                fh = QFile(fPath)
                if  fh.open(QIODevice.ReadOnly):
                    document = QDomDocument()
                
                    if not document.setContent(fh):
                        raise ValueError, "could not parse XML"

                    newModel = ComponentModel(document, self)
                    self.view.setModel(newModel)
                    self.model = newModel
                    self.xmlPath = fPath
                    fi = QFileInfo(fPath);
                    self.name = fi.fileName(); 

                    if self.name[-4:] == '.xml':
                        self.name = self.name[:-4]
            except (IOError, OSError, ValueError), e:
                error = "Failed to import: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()
                    return fPath
            

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    component = ComponentDlg()
    component.resize(640,480)
    component.show()
    component.load()
    app.exec_()

    
