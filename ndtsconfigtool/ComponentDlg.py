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

from Merger import Merger, MergerDlg, IncompatibleNodeError

import os
import time 

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


        ## if merging compited
        self._merged = False

        ## merger dialog
        self.mergerdlg = None

        ## if changes saved
        self.dirty = False
        

    def getNodeRow(self, child, node):
        row = 0
        if node:
            children = node.childNodes()
            for i in range(children.count()):
                ch = children.item(i)
                if child == ch:
                    break
                row += 1
            if row < children.count():
                return row

    def getPathFromNode(self, node):
        ancestors = [node]
        path = [] 

        while ancestors[0].parentNode().nodeName() != '#document':
            ancestors.insert(0, ancestors[0].parentNode())
        ancestors.insert(0, ancestors[0].parentNode())


        parent = None
        for child in ancestors:   
            if parent: 
                row = self.getNodeRow(child, parent)
                path.append((row,unicode(child.nodeName())))
            parent = child    
        return path

    def getPath(self):
        index = self.view.currentIndex()
        pindex = index.parent()
        path = []
        if not index.isValid():
            return 
        row = 1
        while pindex.isValid() and row is not None:
            child = index.internalPointer().node
            parent = pindex.internalPointer().node
            row = self.getNodeRow(child, parent)
            path.insert(0,(row,unicode(child.nodeName())))
            index = pindex
            pindex = pindex.parent()
        
        child = index.internalPointer().node
        row = self.getNodeRow(child, self.document)
        path.insert(0,(row,unicode(child.nodeName())))

        return path
        
    def showNodes(self,nodes):
        for node in nodes:
            path = self.getPathFromNode(node)
            self.selectItem(path)    


    def getIndex(self, path):
        if not path:
            return QModelIndex()
        item = self.view.model().rootItem
        node = item.node
        index = self.view.model().createIndex(0,0,item)
        self.view.expand(index)
        item = index.internalPointer()
        for step in path:
            index = self.view.model().index(step[0],0,index) 
            self.view.expand(index)
            item = index.internalPointer()
        return index    

            
        
    def selectItem(self, path):
        index = self.getIndex(path)
        
        if index and index.isValid():
            self.view.setCurrentIndex(index)
            self.tagClicked(index)
            self.view.expand(index)

    def getState(self):
        path = self.getPath()
        return (self.document.toString(0),path, self.dirty)


    def setState(self,state):
        (xml, path, dirty)=state
        try:
            self.loadFromString(xml)
        except (IOError, OSError, ValueError), e:
            error = "Failed to load: %s" % e
            print error
        self.hideFrame()    
        self.selectItem(path) 
        self.dirty = dirty
            

    def updateForm(self):
        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1,1)
        
        model = ComponentModel(QDomDocument(),self)
        self.view.setModel(model)
        
        self.widget = QWidget()
        self.frameLayout = QGridLayout()
        self.frameLayout.addWidget(self.widget)
        self.frame.setLayout(self.frameLayout)

        


    def applyItem(self):
        if not self.view or not self.view.model() or not self.widget:
            return
        if hasattr(self.widget,'apply'):
            self.widget.apply()
            self.dirty = True


    def nodeToString(self, node):
        doc = QDomDocument()
        child = doc.importNode(node,True)
        doc.appendChild(child)
        return unicode(doc.toString(0))



    def stringToNode(self, xml):
        doc = QDomDocument()
        
        if not unicode(xml).strip():
            return
        if not doc.setContent(unicode(xml).strip()):
            raise ValueError, "could not parse XML"
        if self.document and doc and doc.hasChildNodes():
            return self.document.importNode(doc.firstChild(), True)
                
        
    def pasteItem(self):
        print "pasting item"
        
        if not self.view or not self.view.model() or not self.widget \
                or not hasattr(self.widget,"subItems") :
            ## Message
            return

        clipboard = QApplication.clipboard()
#        print "TEXT: \n",clipboard.text()
        clipNode = self.stringToNode(clipboard.text())
        if clipNode is None:
            return

#        print "TEXT: \n",clipboard.text()
        name = unicode(clipNode.nodeName())

#        print "NAME: ",clipNode.nodeName()
        if name not in self.widget.subItems:
            ## Message
            return        

        index = self.view.currentIndex()
        if not index.isValid():
            return
        sel = index.internalPointer()
        if not sel:
            ## Message
            return

        self.dirty = True
        node = sel.node


        self.widget.node = node
        self.widget.appendNode(clipNode, index)        

        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        
        self.view.expand(index)


        

    def addItem(self,name):
        if not name in self.tagClasses.keys():
            return
        if not self.view or not self.view.model() or not self.widget:
            return
        if not hasattr(self.widget,'subItems') or  name not in self.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return
        self.dirty = True
        node = sel.node
        self.widget.node = node
        child = self.widget.root.createElement(QString(name))
        self.widget.appendNode(child, index)
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        self.view.expand(index)
        return child


    def removeSelectedItem(self):
        if not self.view or not self.view.model() or not self.widget:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return

        self.dirty = True
        node = sel.node

        attributeMap = node.attributes()
        name = ""
        if attributeMap.contains("name"):
            name = attributeMap.namedItem("name").nodeValue()
        print "Removing" , node.nodeName(), name

        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.nodeToString(node))
        
        if hasattr(self.widget,"node"):
            self.widget.node = node.parentNode()

        self.widget.removeNode(node, index.parent())
                
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        if index.parent().isValid():
            self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                            index.parent(),index.parent())


    def copySelectedItem(self):
        if not self.view or not self.view.model() or not self.widget:
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
        print "Copying" , node.nodeName(), name

        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.nodeToString(node))
            

    def createGUI(self):

        self.setupUi(self)


        self.mergerdlg = MergerDlg(self)
        self.mergerdlg.createGUI()

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
        if not item :
            raise Exception, "Unreachable item"
        if not hasattr(item,'node'):
            raise Exception, "Unreachable item"

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
        for column in range(self.view.model().columnCount(index)):
            self.view.resizeColumnToContents(column)

    def collapsed(self,index):
        for column in range(self.view.model().columnCount(index)):
            self.view.resizeColumnToContents(column)

    def setName(self, name, directory = None):
        fi = None
        dr = ""
        if self.componentFile:
            fi = QFileInfo(self.componentFile)
        if directory is None and fi:
            dr = unicode(fi.dir().path())
        else:
            dr = unicode(directory)

        self.componentFile = dr + "/" + name + ".xml"
        print "FN", self.componentFile 
        self.name = name
        self.xmlPath = self.componentFile
        


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
                    self.loadFromString(fh)
                    self.xmlPath = self.componentFile
                    fi = QFileInfo(self.componentFile)
                    self.name = unicode(fi.fileName())

                    if self.name[-4:] == '.xml':
                        self.name = self.name[:-4]
                    self.dirty = False
                    return self.componentFile
            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()




    def set(self, xml):
        self.componentFile = self.directory + "/" + self.name + ".xml"
        self.loadFromString(xml)
        self.xmlPath = self.componentFile
        self.dirty = False
        return self.componentFile



    def loadFromString(self, xml):
        self.document = QDomDocument()
        
        if not self.document.setContent(xml):
            raise ValueError, "could not parse XML"
        
        newModel = ComponentModel(self.document, self)
        self.view.setModel(newModel)
        

    def loadComponentItem(self,filePath = None):
        
        if not self.view or not self.view.model() or not self.widget \
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

        self.dirty = True

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
                        child2 = self.document.importNode(child, True)
                        self.widget.appendNode(child2, index)

#                        node.appendChild(child)
                        child = child.nextSibling()

                        
                self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
                self.view.expand(index)
                    

            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()

            



    def loadDataSourceItem(self,filePath = None):
        print "Loading DataSource"
        
        if not self.view or not self.view.model() or not self.widget \
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
                

        self.dirty = True

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
                            ds2 = self.document.importNode(ds, True)
                            self.widget.appendNode(ds2, index)
#                            node.appendChild(ds)

                self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
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
        
        if not self.view or not self.view.model() or not self.widget \
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


        self.dirty = True


        self.widget.node = node
        dsNode2 = self.document.importNode(dsNode, True)
        self.widget.appendNode(dsNode2, index)
        
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        self.view.expand(index)

    def closeMergerDlg(self):
        if self.mergerdlg:
            self.mergerdlg.accept()


    def merge(self):
        if not self.view or not self.view.model():
            self._merged = False
            return
        if not self.document:
            self._merged = False
            return
        self.dirty = True
        try:
            merger = Merger(self.document)
            self.connect(merger, SIGNAL("finished()"), merger, SLOT("deleteLater()"))
            self.connect(merger, SIGNAL("finished()"), self.closeMergerDlg)
            merger.start()

            self.mergerdlg.exec_()
            while not merger.isFinished():
                time.sleep(0.01)
            
            if merger.exception:
                raise merger.exception
            self._merged = True
            newModel = ComponentModel(self.document, self)
            self.view.setModel(newModel)
            self.hideFrame()

        except IncompatibleNodeError, e: 
            print "Error in Merging: %s" % unicode(e.value)
            self._merged = False
            newModel = ComponentModel(self.document, self)
            self.view.setModel(newModel)
            self.hideFrame()
            if hasattr(e,"nodes") and e.nodes: 
                self.showNodes(e.nodes)
            QMessageBox.warning(self, "Merging problem",
                                "Error in Merging: %s" % unicode(e.value) )
        except  Exception, e:    
            print "Exception: %s" % unicode(e)
            self._merged = False
            newModel = ComponentModel(self.document, self)
            self.view.setModel(newModel)
            self.hideFrame()

        return self._merged

    def hideFrame(self):
        if self.widget:
            self.widget.setVisible(False)
        self.widget = QWidget()
        self.frameLayout.addWidget(self.widget)
        self.widget.show()
        self.frame.show()


    def createHeader(self):
        self.document = QDomDocument()
        self.document = self.document
        processing = self.document.createProcessingInstruction("xml", 'version="1.0"') 
        self.document.appendChild(processing)
        
        definition = self.document.createElement(QString("definition"))
        self.document.appendChild(definition)
        newModel = ComponentModel(self.document, self)
        self.view.setModel(newModel)
        self.hideFrame()
        self.dirty = True 


    def get(self):
        if hasattr(self.document,"toString"):
            return unicode(self.document.toString(0))

    def save(self):
        print "saving"
        if not self._merged:
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
                stream << self.document.toString(2)
                self.dirty = False
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

    def getNewName(self):
        self.componentFile = unicode(
            QFileDialog.getSaveFileName(self,"Save Component As ...",self.componentFile,
                                        "XML files (*.xml);;HTML files (*.html);;"
                                        "SVG files (*.svg);;User Interface files (*.ui)"))
        return self.componentFile
        

    

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    component = ComponentDlg()
    component.resize(640,480)
    component.show()
    component.load()
    app.exec_()

    
