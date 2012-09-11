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
from StrategyDlg import StrategyDlg
from DefinitionDlg import DefinitionDlg

from Merger import Merger, IncompatibleNodeError

import os

from ComponentModel import *    
from LabeledObject import LabeledObject

## dialog defining a tag link 
class ComponentDlg(QDialog,ui_componentdlg.Ui_ComponentDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(ComponentDlg, self).__init__(parent)
        
        self.xmlPath = os.path.dirname("./components/")
        self.componentFile = None
        self.dsPath = os.path.dirname("./datasources/")
        self.directory = ""

        self.view = None
        self.frame = None
        self.model = None
        

        self.actions = None

        ## component id
        self.idc = None
        self.name = ""
        self.fpath = ""


        self._externalSave = None
        self._externalApply = None

        self.tagClasses = {"field":FieldDlg, 
                           "group":GroupDlg, 
                           "definition":DefinitionDlg, 
                           "attribute":RichAttributeDlg,
                           "link":LinkDlg,
                           "datasource":DataSourceDlg,
                           "strategy":StrategyDlg
#                           ,"dimensions":DimensionsDlg
                           }
        self.widget = None

        self.currentTag = None
        self.frameLayout = None

        self.document = None

    def updateForm(self):
        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1,1)
        
        self.model = ComponentModel(QDomDocument(),self)
        self.view.setModel(self.model)
        
        self.widget = QWidget()
#        self.widget.createGUI()

        self.frameLayout = QGridLayout()
        self.frameLayout.addWidget(self.widget)
        self.frame.setLayout(self.frameLayout)


    def applyItem(self):
        if not self.model or not self.view or not self.widget:
            return
        if hasattr(self.widget,'apply'):
            self.widget.apply()
        

    def addItem(self,name):
        if not name in self.tagClasses.keys():
            return
        if not self.model or not self.view or not self.widget:
            return
        if not hasattr(self.widget,'subItems') or  name not in self.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return
        node = sel.node
        self.widget.node = node
        child = self.widget.root.createElement(QString(name))
        self.widget.appendNode(child, index)
        #                        print name, " at ", node.nodeName()
                #                        row=self.widget.getNodeRow(child)
#                        childIndex=self.model.index(row,0,index)
#                        self.view.setCurrentIndex(childIndex)
#                        self.widget = None
#                        self.tagClicked(childIndex)
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        self.view.expand(index)

    def removeSelectedItem(self):
        if not self.model or not self.view or not self.widget:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return

        node = sel.node
        attributeMap = node.attributes()
        name = ""
        if attributeMap.contains("name"):
            name = attributeMap.namedItem("name").nodeValue()

        print "Removing" , node.nodeName(), name
#                node = self.widget.node
        
        
        if hasattr(self.widget,"node"):
            self.widget.node = node.parentNode()

        self.widget.removeNode(node, index.parent())
                
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        if index.parent().isValid():
            self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                            index.parent(),index.parent())
            

    def createGUI(self):

        self.setupUi(self)
        self.updateForm()
        
#        self.connect(self.savePushButton, SIGNAL("clicked()"), self.save)
        self.connect(self.closePushButton, SIGNAL("clicked()"), self.close)
        self.connect(self.view, SIGNAL("activated(QModelIndex)"), self.tagClicked)  
        self.connect(self.view, SIGNAL("clicked(QModelIndex)"), self.tagClicked)  
        self.connect(self.view, SIGNAL("expanded(QModelIndex)"), self.expanded)
        self.connect(self.view, SIGNAL("collapsed(QModelIndex)"), self.collapsed)


    def connectExternalActions(self, externalApply=None , externalSave=None ):
        if externalSave and self._externalSave is None:
            self.connect(self.savePushButton, SIGNAL("clicked()"), 
                         externalSave)
            self._externalSave = externalSave
        if externalApply and self._externalApply is None:
            self._externalApply = externalApply


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

        
        if self.widget:
            self.widget.setVisible(False)
        if unicode(nNode) in self.tagClasses.keys():
            self.frame.hide()
            self.frameLayout.removeWidget(self.widget)
            self.widget = self.tagClasses[unicode(nNode)]()
            self.widget.root = self.document
            self.widget.setFromNode(node)
            self.widget.createGUI()
            if hasattr(self.widget,"connectExternalActions"):
                self.widget.connectExternalActions(self._externalApply)
            if hasattr(self.widget,"treeMode"):
                self.widget.treeMode()
            self.widget.model = self.model
            self.widget.view = self.view
            self.frameLayout.addWidget(self.widget)
            self.widget.show()
#            self.frameLayout.update()
            self.frame.show()
        else:
            self.widget = None
         
    def openMenu(self, position):
        index = self.view.indexAt(position)
        if index.isValid():
            self.tagClicked(index)
        menu = QMenu()
        for action in self.actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.view.viewport().mapToGlobal(position))
                 
   
    def addContextMenu(self,actions):
         self.view.setContextMenuPolicy(Qt.CustomContextMenu)
         self.view.customContextMenuRequested.connect(self.openMenu)
         self.actions = actions

    def expanded(self,index):
        for column in range(self.model.columnCount(index)):
            self.view.resizeColumnToContents(column)

    def collapsed(self,index):
        for column in range(self.model.columnCount(index)):
            self.view.resizeColumnToContents(column)


    def load(self,filePath = None):
        
        if not filePath:
            if not self.name:
                self.componentFile = unicode(QFileDialog.getOpenFileName(
                        self,"Open File",self.xmlPath,
                        "XML files (*.xml);;HTML files (*.html);;"
                        "SVG files (*.svg);;User Interface files (*.ui)"))
            else:
                self.componentFile = self.directory + "/" + self.name + ".xml"
        else:
            self.componentFile = filePath
        if self.componentFile:
            try:
                fh = QFile(self.componentFile)
                if  fh.open(QIODevice.ReadOnly):
                    self.document = QDomDocument()
                
                    if not self.document.setContent(fh):
                        raise ValueError, "could not parse XML"

                    newModel = ComponentModel(self.document, self)
                    self.view.setModel(newModel)
                    self.model = newModel
                    self.xmlPath = self.componentFile
                    fi = QFileInfo(self.componentFile)
                    self.name = fi.fileName() 

                    if self.name[-4:] == '.xml':
                        self.name = self.name[:-4]
                    return self.componentFile
            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()


    def loadComponentItem(self,filePath = None):
        
        if not self.model or not self.view or not self.widget \
                or not hasattr(self.widget, "subItems") or "component" not in  self.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return
        node = sel.node

        if not filePath:
                itemFile = unicode(
                    QFileDialog.getOpenFileName(self,"Open File",self.xmlPath,
                                                "XML files (*.xml);;HTML files (*.html);;"
                                                "SVG files (*.svg);;User Interface files (*.ui)"))
        else:
            itemFile = filePath
        if itemFile:
            try:
                fh = QFile(itemFile)
                if  fh.open(QIODevice.ReadOnly):
                    root = QDomDocument()
                    if not root.setContent(fh):
                        raise ValueError, "could not parse XML"
                    definition = root.firstChildElement(QString("definition"))           
                    child = definition.firstChild()
                    self.widget.node = node

                    while not child.isNull():
                        self.widget.appendNode(child, index)
#                        node.appendChild(child)
                        child = child.nextSibling()

                        
                self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
                self.view.expand(index)
                    

            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()

            



    def loadDataSourceItem(self,filePath = None):
        print "Loading DataSource"
        
        if not self.model or not self.view or not self.widget \
                                or not hasattr(self.widget, "subItems") \
                                or "datasource" not in  self.widget.subItems:
            return

        child = self.widget.node.firstChild()
        while not child.isNull():
            if child.nodeName() == 'datasource':
                QMessageBox.warning(self, "DataSource exists", 
                                    "To add a new datasource please remove the old one")
                return
            child = child.nextSibling()    
                

        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return
        node = sel.node

        if not filePath:
                dsFile = unicode(
                    QFileDialog.getOpenFileName(self,"Open File",self.dsPath,
                                                "XML files (*.xml);;HTML files (*.html);;"
                                                "SVG files (*.svg);;User Interface files (*.ui)"))
        else:
            dsFile = filePath
        if dsFile:
            try:
                fh = QFile(dsFile)
                if  fh.open(QIODevice.ReadOnly):
                    root = QDomDocument()
                    if not root.setContent(fh):
                        raise ValueError, "could not parse XML"
                    definition = root.firstChildElement(QString("definition"))           
                    if definition:
                        ds  = definition.firstChildElement(QString("datasource"))
                        if ds:


                            self.widget.node = node
                            self.widget.appendNode(ds, index)
#                            node.appendChild(ds)

                self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
                self.view.expand(index)
                self.dsPath = dsFile

            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()




    def addDataSourceItem(self, dsNode):
        print "Adding DataSource"
        
        if dsNode.nodeName() != 'datasource':
            return
        
        if not self.model or not self.view or not self.widget \
                or not hasattr(self.widget,"subItems") or "datasource" not in  self.widget.subItems:
            return

        child = self.widget.node.firstChild()
        while not child.isNull():
            if child.nodeName() == 'datasource':
                QMessageBox.warning(self, "DataSource exists", 
                                    "To add a new datasource please remove the old one")
                return
            child = child.nextSibling()    
                

        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return
        node = sel.node


        self.widget.node = node
        self.widget.appendNode(dsNode, index)
        
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        self.view.expand(index)



    def merge(self):
        if not self.model or not self.view or not self.widget:
            return
        if not self.document:
            return
        try:
            mr = Merger(self.document)
            mr.merge()
            self.view.reset()
#            self.view.update()
        except IncompatibleNodeError, e: 
            QMessageBox.warning(self, "Merging problem",
                                "Error in Merging: %s" % unicode(e) )
            print "Error in Merging: %s" % unicode(e)
            return
        except  Exception, e:    
            print "Exception: %s" % unicode(e)
            return
        return True


    def createHeader(self):
            self.document = QDomDocument()
            self.root = self.document
            processing = self.root.createProcessingInstruction("xml", 'version="1.0"') 
            self.root.appendChild(processing)
            
            definition = self.root.createElement(QString("definition"))
            self.root.appendChild(definition)
            newModel = ComponentModel(self.document, self)
            self.view.setModel(newModel)
            self.model = newModel


    def save(self):
        print "saving"
        if not self.merge():
            QMessageBox.warning(self, "Saving problem",
                                "Document not merged" )
            
            return
        error = None
        if self.componentFile:
            try:
                fh = QFile(self.componentFile)
                if not fh.open(QIODevice.WriteOnly):
                    raise IOError, unicode(fh.errorString())
                stream = QTextStream(fh)
                stream <<self.document.toString(2)
#                print self.document.toString(2)
            except (IOError, OSError, ValueError), e:
                error = "Failed to save: %s" % e
                print error
                
            finally:
                if fh is not None:
                    fh.close()


    def close(self):
        if QMessageBox.question(self, "Close component",
                                "Would you like to close the component ?", 
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
#        self.revert()
        self.reject()




    def saveAs(self):
        if not self.merge():
            QMessageBox.warning(self, "Saving problem",
                                "Document not merged" )
            
            return
        error = None
        self.componentFile = unicode(
            QFileDialog.getSaveFileName(self,"Save Component",self.componentFile,
                                        "XML files (*.xml);;HTML files (*.html);;"
                                        "SVG files (*.svg);;User Interface files (*.ui)"))

        
        try:
            fh = QFile(self.componentFile)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError, unicode(fh.errorString())
            stream = QTextStream(fh)
            stream <<self.document.toString(2)
            #                print self.document.toString(2)
            ## TODO change item name
        except (IOError, OSError, ValueError), e:
            error = "Failed to save: %s" % e
            print error
            
        finally:
            if fh is not None:
                fh.close()

    

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    component = ComponentDlg()
    component.resize(640,480)
    component.show()
    component.load()
    app.exec_()

    
