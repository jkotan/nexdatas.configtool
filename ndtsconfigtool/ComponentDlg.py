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

from PyQt4.QtCore import (SIGNAL, SLOT, QModelIndex, QString, Qt, QFileInfo, QFile, QIODevice, 
                          QTextStream)
from PyQt4.QtGui import (QDialog, QWidget, QGridLayout, QApplication, QMenu, QFileDialog,
                         QMessageBox )
from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
                         QXmlInputSource, QXmlSimpleReader)

from ui.ui_componentdlg import Ui_ComponentDlg
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

from ComponentModel import ComponentModel
#from LabeledObject import LabeledObject

## dialog defining a tag link 
class ComponentDlg(QDialog, Ui_ComponentDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(ComponentDlg, self).__init__(parent)

        ## directory from which components are loaded by default
        self.directory = ""
        
        ## component view
        self.view = None

        ## component id
        self.idc = None
        ## component name
        self.name = ""

        ## widget of component item
        self.widget = None

        ## component DOM document
        self.document = None        


        self._xmlPath = os.path.dirname("./components/")
        self._componentFile = None
        self._dsPath = os.path.dirname("./datasources/")

        ## item frame
        self.frame = None
        ## component actions
        self._actions = None

        ## save action
        self._externalSave = None
        ## apply action
        self._externalApply = None

        ## item class shown in the frame
        self._tagClasses = {"field":FieldDlg, 
                           "group":GroupDlg, 
                           "definition":DefinitionDlg, 
                           "attribute":RichAttributeDlg,
                           "link":LinkDlg,
                           "datasource":DataSourceDlg,
                           "strategy":StrategyDlg
#                           ,"dimensions":DimensionsDlg
                           }

        ## current component tag
        self._currentTag = None
        self._frameLayout = None


        ## if merging compited
        self._merged = False

        ## merger dialog
        self._mergerdlg = None
        
        ## merger
        self._merger = None
            
        ## show all attribures or only the type attribute
        self._allAttributes = False
        
        ## saved XML
        self.savedXML = None


    ## checks if not saved
    # \returns True if it is not saved     
    def isDirty(self):
        string = self.get()
        return False if string == self.savedXML else True


    ## provides the row number of the given child item
    # \param child DOM child node
    # \param node DOM parent node
    # \returns the row number of the given child item
    def _getNodeRow(self, child, node):
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


    ## provides the path of component tree for a given node
    # \param node DOM node
    # \returns path represented as a list with elements: (row number, node name)
    def _getPathFromNode(self, node):
        ancestors = [node]
        path = [] 

        while ancestors[0].parentNode().nodeName() != '#document':
            ancestors.insert(0, ancestors[0].parentNode())
        ancestors.insert(0, ancestors[0].parentNode())


        parent = None
        for child in ancestors:   
            if parent: 
                row = self._getNodeRow(child, parent)
                path.append((row, unicode(child.nodeName())))
            parent = child    
        return path


    ## provides the current component tree item
    # \returns DOM node instance
    def _getCurrentNode(self):
        index = self.view.currentIndex()
        if not index.isValid():
            return
        item = index.internalPointer()
        if not item:
            return
        return item.node
        
        
        



    ## provides the path of component tree for the current component tree item
    # \returns path represented as a list with elements: (row number, node name)
    def _getPath(self):
        index = self.view.currentIndex()
        pindex = index.parent()
        path = []
        if not index.isValid():
            return 
        row = 1
        while pindex.isValid() and row is not None:
            child = index.internalPointer().node
            parent = pindex.internalPointer().node
            row = self._getNodeRow(child, parent)
            path.insert(0, (row, unicode(child.nodeName())))
            index = pindex
            pindex = pindex.parent()
        
        child = index.internalPointer().node
        row = self._getNodeRow(child, self.document)
        path.insert(0, (row, unicode(child.nodeName())))

        return path

        
    ## selects and opens the last nodes of the given list in the component tree
    # \param nodes list of DOM nodes 
    def _showNodes(self, nodes):
        for node in nodes:
            path = self._getPathFromNode(node)
            self._selectItem(path)    



    ## provides  index of the component item defiend by the path
    # \param path path represented as a list with elements: (row number, node name)
    # \returns component item index        
    def _getIndex(self, path):
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
            

    ## selectes item defined by path in component tree      
    # \param path path represented as a list with elements: (row number, node name)
    def _selectItem(self, path):
        index = self._getIndex(path)
        
        if index and index.isValid():
            self.view.setCurrentIndex(index)
            self.tagClicked(index)
            self.view.expand(index)

    ## provides the state of the component dialog        
    # \returns tuple with (xml string, path)        
    def getState(self):
        path = self._getPath()
        return (self.document.toString(0),path)


    ## sets the state of the component dialog        
    # \param state tuple with (xml string, path)        
    def setState(self, state):
        (xml, path)=state
        try:
            self._loadFromString(xml)
        except (IOError, OSError, ValueError), e:
            error = "Failed to load: %s" % e
            print error
        self._hideFrame()    
        self._selectItem(path) 
            

    ## updates the component dialog
    # \brief It creates model and frame item    
    def updateForm(self):
        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1,1)
        
        model = ComponentModel(QDomDocument(),self._allAttributes,self)
        self.view.setModel(model)
        
        self.widget = QWidget()
        self._frameLayout = QGridLayout()
        self._frameLayout.addWidget(self.widget)
        self.frame.setLayout(self._frameLayout)

        

    ## applies component item
    # \brief it checks if item widget exists and calls apply of the item widget
    def applyItem(self):
        if not self.view or not self.view.model() or not self.widget:
            return
        if not hasattr(self.widget,'apply'):
            return
        self.widget.apply()
        self.view.resizeColumnToContents(0)
        self.view.resizeColumnToContents(1)
        return True

    ## converts DOM node to XML string
    # \param component DOM node
    # \returns XML string
    def _nodeToString(self, node):
        doc = QDomDocument()
        child = doc.importNode(node,True)
        doc.appendChild(child)
        return unicode(doc.toString(0))



    ## converts XML string to DOM node 
    # \param xml XML string
    # \returns component DOM node
    def _stringToNode(self, xml):
        doc = QDomDocument()
        
        if not unicode(xml).strip():
            return
        if not doc.setContent(unicode(xml).strip()):
            raise ValueError, "could not parse XML"
        if self.document and doc and doc.hasChildNodes():
            return self.document.importNode(doc.firstChild(), True)
                
        
    ## pastes the component item from the clipboard into the component tree
    # \returns True on success    
    def pasteItem(self):
        print "pasting item"
        
        if not self.view or not self.view.model() or not self.widget \
                or not hasattr(self.widget,"subItems") :
            ## Message
            return

        clipboard = QApplication.clipboard()
#        print "TEXT: \n",clipboard.text()
        clipNode = self._stringToNode(clipboard.text())
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

        node = sel.node


        self.widget.node = node
        self.widget.appendNode(clipNode, index)        

        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        
        self.view.expand(index)
        return True

        

    ## creates the component item with the given name in the component tree
    # \param name component item name
    # \returns component DOM node related to the new item
    def addItem(self, name):
        if not name in self._tagClasses.keys():
            return
        if not self.view or not self.view.model() or not self.widget:
            return
        if not hasattr(self.widget,'subItems') or  name not in self.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node
        self.widget.node = node
        child = self.widget.root.createElement(QString(name))
        self.widget.appendNode(child, index)
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        self.view.expand(index)
        return child


    ## removes the currenct component tree item if possible
    # \returns True on success
    def removeSelectedItem(self):
        if not self.view or not self.view.model() or not self.widget:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return

        node = sel.node

        attributeMap = node.attributes()
        name = ""
        if attributeMap.contains("name"):
            name = attributeMap.namedItem("name").nodeValue()
        print "Removing" , node.nodeName(), name

        
        clipboard = QApplication.clipboard()
        clipboard.setText(self._nodeToString(node))
        
        if hasattr(self.widget,"node"):
            self.widget.node = node.parentNode()

        self.widget.removeNode(node, index.parent())
                
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        if index.parent().isValid():
            self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                            index.parent(),index.parent())
            self.tagClicked(index.parent())
        else:
            self.tagClicked(QModelIndex())
            
        return True    


    ## copies the currenct component tree item if possible
    # \returns True on success
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
        clipboard.setText(self._nodeToString(node))
        return True    


    ## creates GUI
    # It calls setupUi and creates required action connections
    def createGUI(self):

        self.setupUi(self)


        self._mergerdlg = MergerDlg(self)
        self._mergerdlg.createGUI()

        self.updateForm()

#        self.connect(self.savePushButton, SIGNAL("clicked()"), self.save)
        self.connect(self.closePushButton, SIGNAL("clicked()"), self._close)
        self.connect(self.view, SIGNAL("activated(QModelIndex)"), self.tagClicked)  
        self.connect(self.view, SIGNAL("clicked(QModelIndex)"), self.tagClicked)  
        self.connect(self.view, SIGNAL("expanded(QModelIndex)"), self._resizeColumns)
        self.connect(self.view, SIGNAL("collapsed(QModelIndex)"), self._resizeColumns)



    ## connects external actions
    # \brief It connects the save action and stores the apply action
    def connectExternalActions(self, externalApply=None , externalSave=None ):
        if externalSave and self._externalSave is None:
            self.connect(self.savePushButton, SIGNAL("clicked()"), 
                         externalSave)
            self._externalSave = externalSave
        if externalApply and self._externalApply is None:
            self._externalApply = externalApply


    # switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status):
        if status == self._allAttributes:
            return
        self._allAttributes = status
        if hasattr(self,"view"):
             model = self.view.model()   
             model.setAttributeView(self._allAttributes)
#             self.view.reset()
             newModel = ComponentModel(self.document, self._allAttributes ,self)
             self.view.setModel(newModel)
             self._hideFrame()


    ## sets selected component item in the item frame
    # \brief It is executed  when component tree item is selected
    # \param index of component tree item
    def tagClicked(self, index):
        self._currentTag = index
        item  = self._currentTag.internalPointer()
        if not item:
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
        if unicode(nNode) in self._tagClasses.keys():
            self.frame.hide()
            self._frameLayout.removeWidget(self.widget)
            self.widget = self._tagClasses[unicode(nNode)]()
            self.widget.root = self.document
            self.widget.setFromNode(node)
            self.widget.createGUI()
            if hasattr(self.widget,"connectExternalActions"):
                self.widget.connectExternalActions(self._externalApply)
            if hasattr(self.widget,"treeMode"):
                self.widget.treeMode()
            self.widget.view = self.view
            self._frameLayout.addWidget(self.widget)
            self.widget.show()
#            self._frameLayout.update()
            self.frame.show()
        else:
            self.widget = None


    ## opens context Menu        
    # \param position in the component tree
    def _openMenu(self, position):
        index = self.view.indexAt(position)
        if index.isValid():
            self.tagClicked(index)
        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.view.viewport().mapToGlobal(position))
       
          
    ## sets up context menu
    # \param actions list of the context menu actions
    def addContextMenu(self, actions):
         self.view.setContextMenuPolicy(Qt.CustomContextMenu)
         self.view.customContextMenuRequested.connect(self._openMenu)
         self._actions = actions

    ## resizes column size after tree item expansion     
    # \param index index of the expanded item
    def _resizeColumns(self, index):
        for column in range(self.view.model().columnCount(index)):
            self.view.resizeColumnToContents(column)


    ## sets name and directory of the current component
    # \param name component name
    # \param directory component directory       
    def setName(self, name, directory = None):
        fi = None
        dr = ""
        if self._componentFile:
            fi = QFileInfo(self._componentFile)
        if directory is None and fi:
            dr = unicode(fi.dir().path())
        elif directory:
            dr = unicode(directory)
        elif self.directory:
            dr = self.directory
        else:
            dr = '.'
        
        self._componentFile = dr + "/" + name + ".xml"
        self.name = name
        self._xmlPath = self._componentFile
        

    ## loads the component from the file 
    # \param filePath xml file name with full path    
    def load(self,filePath = None):
        
        if not filePath:
            if not self.name:
                self._componentFile = unicode(QFileDialog.getOpenFileName(
                        self,"Open File",self._xmlPath,
                        "XML files (*.xml);;HTML files (*.html);;"
                        "SVG files (*.svg);;User Interface files (*.ui)"))
            else:
                self._componentFile = self.directory + "/" + self.name + ".xml"
        else:
            self._componentFile = filePath
        if self._componentFile:
            try:
                fh = QFile(self._componentFile)
                if  fh.open(QIODevice.ReadOnly):
                    self._loadFromString(fh)
                    self._xmlPath = self._componentFile
                    fi = QFileInfo(self._componentFile)
                    self.name = unicode(fi.fileName())

                    if self.name[-4:] == '.xml':
                        self.name = self.name[:-4]
                    self.savedXML = self.get()
                    return self._componentFile
            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()



    ## sets component from XML string and reset component file name
    # \param xml XML string               
    def set(self, xml):
        self._componentFile = self.directory + "/" + self.name + ".xml"
        self._loadFromString(xml)
        self._xmlPath = self._componentFile
        self.savedXML = self.get()
        return self._componentFile


    ## sets component from XML string
    # \param xml XML string               
    def _loadFromString(self, xml):
        self.document = QDomDocument()
        
        if not self.document.setContent(xml):
            raise ValueError, "could not parse XML"
        children = self.document.childNodes()
        for i in range(children.count()):
            ch = children.item(i)
            if ch.nodeName() == 'xml':
                self.document.removeChild(ch)
        newModel = ComponentModel(self.document,self._allAttributes, self)
        self.view.setModel(newModel)
        

    ## loads the component item from the xml file 
    # \param filePath xml file name with full path    
    def loadComponentItem(self,filePath = None):
        
        if not self.view or not self.view.model() or not self.widget \
                or not hasattr(self.widget, "subItems") or "component" not in  self.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node

        if not filePath:
                itemFile = unicode(
                    QFileDialog.getOpenFileName(self,"Open File",self._xmlPath,
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

        return True    



    ## loads the datasource item from the xml file 
    # \param filePath xml file name with full path    
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
                


        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node

        if not filePath:
                dsFile = unicode(
                    QFileDialog.getOpenFileName(self,"Open File",self._dsPath,
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
                self._dsPath = dsFile

            except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s" % e
                print error
            finally:                 
                if fh is not None:
                    fh.close()

        return True


    ## add the datasource into the component tree
    # \param dsNode datasource DOM node
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
        if not sel or not index.isValid():
            return
        node = sel.node




        self.widget.node = node
        dsNode2 = self.document.importNode(dsNode, True)
        self.widget.appendNode(dsNode2, index)
        
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
        self.view.expand(index)
        return True

    ## accepts merger dialog and interrupts merging
    # \brief It is connected to closing Merger dialog
    def _closeMergerDlg(self):
        if self._mergerdlg:
            self._mergerdlg.accept()

            self._interruptMerger

            
    ## interrupts merging
    # \brief It sets running flag of Merger to False
    def _interruptMerger(self):
        if self._merger:
            self._merger.running = False

    ## merges the component tree
    # \returns True on success
    def merge(self):
        if not self.view or not self.view.model():
            self._merged = False
            return
        if not self.document:
            self._merged = False
            return
        try:
            self._merger = Merger(self.document)
            self.connect(self._merger, SIGNAL("finished()"), self._merger, SLOT("deleteLater()"))
            self.connect(self._merger, SIGNAL("finished()"), self._closeMergerDlg)
            self.connect(self._mergerdlg, SIGNAL("finished(int)"), self._interruptMerger)
            cNode = self._getCurrentNode()
            if cNode:
                print "NODE", cNode.nodeName()
                self._merger.selectedNode = cNode
            self._merger.start()

            self._mergerdlg.exec_()
            while not self._merger.isFinished():
                time.sleep(0.01)
            
            if self._merger.exception:
                raise self._merger.exception

            self._merger = None

            self._merged = True
            newModel = ComponentModel(self.document, self._allAttributes ,self)
            self.view.setModel(newModel)
            self._hideFrame()
            print "NN"
            if  self._merger.selectedNode:
                print "NODE2",  self._merger.selectedNode.nodeName()
            if hasattr(self._merger, "selectedNode") and self._merger.selectedNode: 

                self._showNodes(self._merger.selectedNode)

        except IncompatibleNodeError, e: 
            print "Error in Merging: %s" % unicode(e.value)
            self._merger = None
            self._merged = False
            newModel = ComponentModel(self.document, self._allAttributes, self)
            self.view.setModel(newModel)
            self._hideFrame()
            if hasattr(e, "nodes") and e.nodes: 
                self._showNodes(e.nodes)
            QMessageBox.warning(self, "Merging problem",
                                "Error in Merging: %s" % unicode(e.value) )
        except  Exception, e:    
            print "Exception: %s" % unicode(e)
            self._merged = False
            newModel = ComponentModel(self.document, self._allAttributes, self)
            self.view.setModel(newModel)
            self._hideFrame()
            QMessageBox.warning(self, "Warning",
                                "%s" % unicode(e) )
 
        return self._merged


    ## hides the component item frame
    # \brief It puts an empty widget into the widget frame
    def _hideFrame(self):
        if self.widget:
            self.widget.setVisible(False)
        self.widget = QWidget()
        self._frameLayout.addWidget(self.widget)
        self.widget.show()
        self.frame.show()

        
    ## creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        self.document = QDomDocument()
        self.document = self.document
        
        definition = self.document.createElement(QString("definition"))
        self.document.appendChild(definition)
        newModel = ComponentModel(self.document, self._allAttributes, self)
        self.view.setModel(newModel)
        self._hideFrame()


    ## provides the component in xml string
    # \param indent number of added spaces during pretty printing
    # \returns xml string    
    def get(self, indent=0):
        if hasattr(self.document,"toString"):
            processing = self.document.createProcessingInstruction("xml", 'version="1.0"') 
            self.document.insertBefore(processing, self.document.firstChild())
            string = unicode(self.document.toString(indent))
            self.document.removeChild(processing)
            return string


    ## saves the component
    # \brief It saves the component in the xml file 
    def save(self):
        if not self._merged:
            QMessageBox.warning(self, "Saving problem",
                                "Document not merged" )
            return
        error = None
        if self._componentFile is None:
            self.setName(self.name, self.directory)
        print "saving ", self._componentFile
        try:
            fh = QFile(self._componentFile)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError, unicode(fh.errorString())
            stream = QTextStream(fh)
            string  = self.get(2)
            if string:
                stream << string
            else:
                raise ErrorValue, "Empty component"
    
            self.savedXML = self.get()
            #                print self.document.toString(2)
        except (IOError, OSError, ValueError), e:
            error = "Failed to save: %s" % e
            print error
        finally:
            if fh is not None:
                fh.close()
        if not error:
            return True

    # asks if component should be removed from the component list
    # \brief It is called on removing  the component from the list
    def _close(self):
        if QMessageBox.question(self, "Close component",
                                "Would you like to close the component ?", 
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        self.reject()


    ## provides the component name with its path
    # \returns component name with its path 
    def getNewName(self):
        if self._componentFile is None:
            self.setName(self.name, self.directory)

        self._componentFile = unicode(
            QFileDialog.getSaveFileName(self,"Save Component As ...",self._componentFile,
                                        "XML files (*.xml);;HTML files (*.html);;"
                                        "SVG files (*.svg);;User Interface files (*.ui)"))
        return self._componentFile
        

## test function
def test():
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    component = ComponentDlg()
    component.resize(640, 480)
    component.show()
    component.load()
    app.exec_()

    

if __name__ == "__main__":
    test()
    
