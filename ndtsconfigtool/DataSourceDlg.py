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
## \file DataSourceDlg.py
# Data Source dialog class

import re
import os
from PyQt4.QtCore import (SIGNAL, QModelIndex, QString, Qt, QFileInfo, QFile, QIODevice, 
                          QTextStream, QVariant)
from PyQt4.QtGui import (QApplication, QFileDialog, QMessageBox, QTableWidgetItem, QWidget)
from ui.ui_datasourcedlg import Ui_DataSourceDlg
from PyQt4.QtXml import (QDomDocument, QDomNode)
from NodeDlg import NodeDlg 
import copy
import gc

from Errors import ParameterError

## dialog defining commmon datasource
class CommonDataSourceDlg(NodeDlg):
    
    ## constructor
    # \param datasource instance
    # \param parent patent instance
    def __init__(self, datasource, parent=None):
        super(CommonDataSourceDlg, self).__init__(parent)

        ##  datasource instance
        self.datasource = datasource

        ## database parameters
        self.dbParam = {}

        ## allowed subitems
        self.subItems = ["record", "doc", "device", "database", "query"]

        ## user interface
        self.ui = Ui_DataSourceDlg()


    ## sets focus on save button
    # \brief It sets focus on save button
    def setSaveFocus(self):
        if self.ui :
            self.ui.savePushButton.setFocus()


    ## updates group user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self, text):
        if text == 'CLIENT':
            enable = not self.ui.cRecNameLineEdit.text().isEmpty()
            self.ui.applyPushButton.setEnabled(enable)
            self.ui.savePushButton.setEnabled(enable)
            self.ui.storePushButton.setEnabled(enable)
        elif text == 'DB':
            enable = not self.ui.dQueryLineEdit.text().isEmpty()
            self.ui.applyPushButton.setEnabled(enable)
            self.ui.savePushButton.setEnabled(enable)
            self.ui.storePushButton.setEnabled(enable)
        elif text == 'TANGO':    
            enable = not self.ui.tDevNameLineEdit.text().isEmpty() and \
                not self.ui.tMemberNameLineEdit.text().isEmpty()
            self.ui.applyPushButton.setEnabled(enable)
            self.ui.savePushButton.setEnabled(enable)
            self.ui.storePushButton.setEnabled(enable)
        else:
            ## Additional non-supported frame
            enable = True
            self.ui.applyPushButton.setEnabled(enable)
            self.ui.savePushButton.setEnabled(enable)
            self.ui.storePushButton.setEnabled(enable)

    ## shows and hides frames according to typeComboBox
    # \param text the edited text   
    def setFrames(self,text):
        if text == 'CLIENT':
            self.ui.clientFrame.show()
            self.ui.dbFrame.hide()
            self.ui.tangoFrame.hide()
        elif text == 'TANGO':
            self.ui.clientFrame.hide()
            self.ui.dbFrame.hide()
            self.ui.tangoFrame.show()
        elif text == 'DB':
            self.ui.clientFrame.hide()
            self.ui.dbFrame.show()
            self.ui.tangoFrame.hide()
            self.populateParameters()
            
        self.updateUi(text)


    ## connects the dialog actions 
    def connectWidgets(self):
        

        self.connect(self.ui.typeComboBox, SIGNAL("currentIndexChanged(QString)"), self.setFrames)

        self.connect(self.ui.cRecNameLineEdit, SIGNAL("textChanged(QString)"), self.__cRecNameLineEdit)
        self.connect(self.ui.tDevNameLineEdit, SIGNAL("textChanged(QString)"), self.__tDevNameLineEdit)
        self.connect(self.ui.tMemberNameLineEdit, SIGNAL("textChanged(QString)"), self.__tMemberNameLineEdit)
        self.connect(self.ui.dQueryLineEdit, SIGNAL("textChanged(QString)"), self.__dQueryLineEdit)


        
        self.connect(self.ui.dParamComboBox, SIGNAL("currentIndexChanged(QString)"), 
                     self.__dParamComboBox)

        self.connect(self.ui.dAddPushButton, SIGNAL("clicked()"), self.__addParameter)
        self.connect(self.ui.dRemovePushButton, SIGNAL("clicked()"), self.__removeParameter)
        self.connect(self.ui.dParameterTableWidget, SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.__tableItemChanged)




    ## calls updateUi when the name text is changing
    def __cRecNameLineEdit(self):
        combo = unicode(self.ui.typeComboBox.currentText())
        self.updateUi(combo)


    ## calls updateUi when the name text is changing
    def __dQueryLineEdit(self):
        combo = unicode(self.ui.typeComboBox.currentText())
        self.updateUi(combo)



    ## calls updateUi when the name text is changing
    def __tDevNameLineEdit(self):
        combo = unicode(self.ui.typeComboBox.currentText())
        self.updateUi(combo)


    ## calls updateUi when the name text is changing
    def __tMemberNameLineEdit(self):
        combo = unicode(self.ui.typeComboBox.currentText())
        self.updateUi(combo)


        

    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def __dParamComboBox(self, text):
        param = unicode(text)
        if param == 'DB password':
            QMessageBox.warning(self, "Unprotected password", "Please note that there is no support for any password protection")
            
        self.populateParameters(unicode(text))


    ## adds an parameter    
    #  \brief It runs the Parameter Dialog and fetches parameter name and value    
    def __addParameter(self):
        name =  unicode(self.ui.dParamComboBox.currentText())
        if name not in self.dbParam.keys():
            self.dbParam[name] = ""
        self.populateParameters(name)
    

    ## takes a name of the current parameter
    # \returns name of the current parameter
    def __currentTableParameter(self):
        item = self.ui.dParameterTableWidget.item(self.ui.dParameterTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()


    ## removes an parameter    
    #  \brief It removes the current parameter asking before about it
    def __removeParameter(self):
        param = self.__currentTableParameter()
        if param is None:
            return
        if QMessageBox.question(self, "Parameter - Remove",
                                "Remove parameter: %s = \'%s\'".encode() 
                                %  (param, self.dbParam[unicode(param)]),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes )  == QMessageBox.No :
            return
        if unicode(param) in self.dbParam.keys():
            self.dbParam.pop(unicode(param))
            self.populateParameters()


    ## changes the current value of the parameter        
    # \brief It changes the current value of the parameter and informs the user that parameter names arenot editable
    def __tableItemChanged(self, item):
        param = self.__currentTableParameter()
        if unicode(param)  not in self.dbParam.keys():
            return
        column = self.ui.dParameterTableWidget.currentColumn()
        if column == 1:
            self.dbParam[unicode(param)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Parameter name is not editable", "To change the parameter name, please remove the parameter and add the new one")
        self.populateParameters()





    ## fills in the paramter table      
    # \param selectedParameter selected parameter
    def populateParameters(self, selectedParameter = None):
        selected = None
        self.ui.dParameterTableWidget.clear()
        self.ui.dParameterTableWidget.setSortingEnabled(False)
        self.ui.dParameterTableWidget.setRowCount(len(self.dbParam))
        headers = ["Name", "Value"]
        self.ui.dParameterTableWidget.setColumnCount(len(headers))
        self.ui.dParameterTableWidget.setHorizontalHeaderLabels(headers)	
        for row, name in enumerate(self.dbParam):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.ui.dParameterTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self.dbParam[name])
            if selectedParameter is not None and selectedParameter == name:
                selected = item2
            self.ui.dParameterTableWidget.setItem(row, 1, item2)
        self.ui.dParameterTableWidget.setSortingEnabled(True)
        self.ui.dParameterTableWidget.resizeColumnsToContents()
        self.ui.dParameterTableWidget.horizontalHeader().setStretchLastSection(True);
        if selected is not None:
            selected.setSelected(True)
            self.ui.dParameterTableWidget.setCurrentItem(selected)
            self.ui.dParameterTableWidget.editItem(selected)



    ## closes the window and cleans the dialog label
    # \param event closing event
    def closeEvent(self, event):
        if hasattr(self.datasource.dialog,"clearDialog"):
            self.datasource.dialog.clearDialog()
        self.datasource.dialog = None
        if hasattr(self.datasource,"clearDialog"):
            self.datasource.clearDialog()
        event.accept()    



        
## dialog defining datasource
class DataSourceMethods(object):

    ## constructor
    # \param dialog datasource dialog 
    # \param datasource data 
    def __init__(self, dialog, datasource):

        ## datasource dialog
        self.dialog = dialog

        ## datasource data
        self.datasource = datasource

        ## parameter map for xml tags
        self.__dbmap = {"dbname":"DB name",
                      "hostname":"DB host",
                      "port":"DB port",
                      "user":"DB user",
                      "passwd":"DB password",
                      "mycnf":"Mysql cnf",
                      "mode":"Oracle mode"
                     } 
        self.__idbmap = dict(zip(self.__dbmap.values(), self.__dbmap.keys()))

    ## clears the dialog
    # \brief It sets dialog to None
    def setDialog(self, dialog = None):
        self.dialog = dialog

    ## rejects the changes
    # \brief It asks for the cancellation  and reject the changes
    def close(self):
        if QMessageBox.question(self.dialog, "Close datasource",
                                "Would you like to close the datasource?", 
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return
        self.updateForm()
        self.dialog.reject()


    ##  resets the form
    # \brief It reverts form variables to the last accepted ones    
    def reset(self):
        self.updateForm()


    ## updates the datasource self.dialog
    # \brief It sets the form local variables
    def updateForm(self):    

        if not self.dialog or not self.datasource:
            raise ParameterError, "updateForm parameters not defined"
        if self.datasource.doc is not None:
            self.dialog.ui.docTextEdit.setText(self.datasource.doc)

        if self.datasource.dataSourceType is not None:
            index = self.dialog.ui.typeComboBox.findText(unicode(self.datasource.dataSourceType))
            if  index > -1 :
                self.dialog.ui.typeComboBox.setCurrentIndex(index)
            else:
                self.datasource.dataSourceType = 'CLIENT'    
    
        if self.datasource.dataSourceName is not None:
            self.dialog.ui.nameLineEdit.setText(self.datasource.dataSourceName)

        if self.datasource.clientRecordName is not None:
            self.dialog.ui.cRecNameLineEdit.setText(self.datasource.clientRecordName)

        if self.datasource.tangoDeviceName is not None:
            self.dialog.ui.tDevNameLineEdit.setText(self.datasource.tangoDeviceName)
        if self.datasource.tangoMemberName is not None:
            self.dialog.ui.tMemberNameLineEdit.setText(self.datasource.tangoMemberName)
        if self.datasource.tangoMemberType is not None:
            index = self.dialog.ui.tMemberComboBox.findText(unicode(self.datasource.tangoMemberType))
            if  index > -1 :
                self.dialog.ui.tMemberComboBox.setCurrentIndex(index)
            else:
                self.datasource.tangoMemberType = 'attribute'    
        if self.datasource.tangoHost is not None:
            self.dialog.ui.tHostLineEdit.setText(self.datasource.tangoHost)
        if self.datasource.tangoPort is not None:
            self.dialog.ui.tPortLineEdit.setText(self.datasource.tangoPort)
        if self.datasource.tangoEncoding is not None:
            self.dialog.ui.tEncodingLineEdit.setText(self.datasource.tangoEncoding)



        if self.datasource.dbType  is not None:
            index = self.dialog.ui.dTypeComboBox.findText(unicode(self.datasource.dbType))
            if  index > -1 :
                self.dialog.ui.dTypeComboBox.setCurrentIndex(index)
            else:
                self.datasource.dbType = 'MYSQL'    
        if self.datasource.dbDataFormat is not None:
            index = self.dialog.ui.dFormatComboBox.findText(unicode(self.datasource.dbDataFormat))
            if  index > -1 :
                self.dialog.ui.dFormatComboBox.setCurrentIndex(index)
            else:
                self.datasource.dbDataFormat = 'INIT'    
        
        if self.datasource.dbQuery is not None:        
            self.dialog.ui.dQueryLineEdit.setText(self.datasource.dbQuery)
                
        
        self.dialog.dbParam = {}
        for par in self.datasource.dbParameters.keys():
            index = self.dialog.ui.dParamComboBox.findText(unicode(par))
            if  index < 0 :
                QMessageBox.warning(self.dialog, "Unregistered parameter", 
                                    "Unknown parameter %s = '%s' will be removed." 
                                    % (par, self.datasource.dbParameters[unicode(par)]) )
                self.datasource.dbParameters.pop(unicode(par))
            else:
                self.dialog.dbParam[unicode(par)]=self.datasource.dbParameters[(unicode(par))]
        self.dialog.populateParameters()
        self.dialog.setFrames(self.datasource.dataSourceType)
    
    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if enable:
            self.dialog.ui.closeSaveFrame.hide()
#            self.datasource.nameFrame.show()
            self.datasource.tree = True
        else:
            self.datasource.tree = False
            self.dialog.ui.closeSaveFrame.show()
#            self.datasource.nameFrame.hide()
            
        
    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        if self.dialog and self.dialog.ui and not hasattr(self.dialog.ui,"resetPushButton"):
            self.dialog.ui.setupUi(self.dialog)


        self.updateForm()
        self.dialog.resize(460, 440)

        if not self.datasource.tree :
            self.dialog.connect(self.dialog.ui.resetPushButton, SIGNAL("clicked()"), self.reset)
        else:
            self.dialog.connect(self.dialog.ui.resetPushButton, SIGNAL("clicked()"), self.dialog.reset)
#        self.dialog.connect(self.dialog.closePushButton, SIGNAL("clicked()"), self.close)

        self.dialog.connectWidgets()
        self.dialog.setFrames(self.datasource.dataSourceType)

#        self.datasource.treeMode(datasource.tree)


            
            

            

    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg class
            self.dialog.node = node
            if self.dialog:
                self.dialog.node = node
        attributeMap = self.dialog.node.attributes()
        
        value = attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else ""

        if attributeMap.contains("name"):
            self.datasource.dataSourceName = attributeMap.namedItem("name").nodeValue()
        
        if value == 'CLIENT':
            self.datasource.dataSourceType = unicode(value)

            record = self.dialog.node.firstChildElement(QString("record"))           
            if record.nodeName() != "record":
                QMessageBox.warning(self.dialog, "Internal error", 
                                    "Missing <record> tag")
            else:
                attributeMap = record.attributes()
                self.datasource.clientRecordName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                if attributeMap.contains("name") else "")
                


        elif value == 'TANGO':
            self.datasource.dataSourceType = unicode(value)

            record = self.dialog.node.firstChildElement(QString("record"))
            if record.nodeName() != "record":
                QMessageBox.warning(self.dialog, "Internal error", 
                                    "Missing <record> tag")
            else:
                attributeMap = record.attributes()
                self.datasource.tangoMemberName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                              if attributeMap.contains("name") else "")

            device = self.dialog.node.firstChildElement(QString("device"))
            if device.nodeName() != "device":
                QMessageBox.warning(self.dialog, "Internal error", 
                                    "Missing <device> tag")
            else:
                attributeMap = device.attributes()
                self.datasource.tangoDeviceName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                              if attributeMap.contains("name") else "")
                self.datasource.tangoMemberType = unicode(attributeMap.namedItem("member").nodeValue() \
                                                              if attributeMap.contains("member") else "attribute")
                self.datasource.tangoHost = unicode(attributeMap.namedItem("hostname").nodeValue() \
                                                        if attributeMap.contains("hostname") else "")
                self.datasource.tangoPort = unicode(attributeMap.namedItem("port").nodeValue() \
                                                        if attributeMap.contains("port") else "")
                self.datasource.tangoEncoding = unicode(attributeMap.namedItem("encoding").nodeValue() \
                                                            if attributeMap.contains("encoding") else "")

                                    
        elif value == 'DB':
            self.datasource.dataSourceType = unicode(value)
            
            database = self.dialog.node.firstChildElement(QString("database"))           
            if database.nodeName() != "database":
                QMessageBox.warning(self.dialog, "Internal error", 
                                    "Missing <database> tag")
            else:
                attributeMap = database.attributes()

                for i in range(attributeMap.count()):
                    name = unicode(attributeMap.item(i).nodeName())
                    if name == 'dbtype':
                        self.datasource.dbType = unicode(attributeMap.item(i).nodeValue())
                    elif name in self.__dbmap:
                        self.datasource.dbParameters[self.__dbmap[name]] = unicode(attributeMap.item(i).nodeValue())
                        self.dialog.dbParam[self.__dbmap[name]] = unicode(attributeMap.item(i).nodeValue())

                    
            if not self.datasource.dbType:
                self.datasource.dbType = 'MYSQL'
                    
            text = unicode(self.dialog.dts.getText(database))
            self.datasource.dbParameters['Oracle DSN'] = unicode(text).strip() if text else ""
            self.dialog.dbParam['Oracle DSN'] = unicode(text).strip() if text else ""


            query = self.dialog.node.firstChildElement(QString("query"))
            if query.nodeName() != "query":
                QMessageBox.warning(self.dialog, "Internal error", 
                                    "Missing <query> tag")
            else:
                attributeMap = query.attributes()

                self.datasource.dbDataFormat = unicode(attributeMap.namedItem("format").nodeValue() \
                                                           if attributeMap.contains("format") else "SCALAR")


            text = unicode(self.dialog.dts.getText(query))
            self.datasource.dbQuery = unicode(text).strip() if text else ""


        doc = self.dialog.node.firstChildElement(QString("doc"))           
        text = self.dialog.dts.getText(doc)    
        self.datasource.doc = unicode(text).strip() if text else ""









    ## accepts input text strings
    # \brief It copies the parameters and accept the self.dialog
    def apply(self):

        self.datasource.applied = False
        sourceType = unicode(self.dialog.ui.typeComboBox.currentText())
        self.datasource.dataSourceName = unicode(self.dialog.ui.nameLineEdit.text())

        if sourceType == 'CLIENT':
            recName = unicode(self.dialog.ui.cRecNameLineEdit.text())

            if not recName:
                QMessageBox.warning(self.dialog, "Empty record name", 
                                    "Please define the record name")
                self.dialog.ui.cRecNameLineEdit.setFocus()
                return
            self.datasource.clientRecordName = recName
        elif sourceType == 'TANGO':
            devName = unicode(self.dialog.ui.tDevNameLineEdit.text())
            memName = unicode(self.dialog.ui.tMemberNameLineEdit.text())
            if not devName: 
                QMessageBox.warning(self.dialog, "Empty device name", 
                                    "Please define the device name")
                self.dialog.ui.tDevNameLineEdit.setFocus()
                return
            if not memName:
                QMessageBox.warning(self.dialog, "Empty member name", 
                                    "Please define the member name")
                self.dialog.ui.tMemberNameLineEdit.setFocus()
                return
            self.datasource.tangoDeviceName = devName
            self.datasource.tangoMemberName = memName
            self.datasource.tangoMemberType = unicode(self.dialog.ui.tMemberComboBox.currentText())
            self.datasource.tangoHost = unicode(self.dialog.ui.tHostLineEdit.text())
            self.datasource.tangoPort = unicode(self.dialog.ui.tPortLineEdit.text())
            self.datasource.tangoEncoding = unicode(self.dialog.ui.tEncodingLineEdit.text())
                
        elif sourceType == 'DB':

            if not query:
                QMessageBox.warning(self, "Empty query", 
                                    "Please define the DB query")
                self.datasource.dQueryLineEdit.setFocus()
                return
            self.datasource.dbQuery = query
            self.datasource.dbType =  unicode(self.dialog.ui.dTypeComboBox.currentText())
            self.datasource.dbDataFormat =  unicode(self.dialog.ui.dFormatComboBox.currentText())

            self.datasource.dbParameters.clear()
            for par in self.dialog.dbParam.keys():
                self.datasource.dbParameters[par] = self.dialog.dbParam[par]


        self.datasource.dataSourceType = sourceType

        self.datasource.doc = unicode(self.dialog.ui.docTextEdit.toPlainText()).strip()

        index = QModelIndex()
        if hasattr(self.dialog,"view") and self.dialog.view and self.dialog.view.model():
            if hasattr(self.dialog.view,"currentIndex"):
                index = self.dialog.view.currentIndex()


                finalIndex = self.dialog.view.model().createIndex(index.row(),2,index.parent().internalPointer())
                self.dialog.view.expand(index)    


        row = index.row()
        column = index.column()
        parent = index.parent()

        if self.dialog.root :
            self.updateNode(index)
                
            if index.isValid():
                index = self.dialog.view.model().index(row, column, parent)
                self.dialog.view.setCurrentIndex(index)
                self.dialog.view.expand(index)
        
            if hasattr(self.dialog,"view")  and self.dialog.view and self.dialog.view.model():
                self.dialog.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index.parent(),index.parent())
                if  index.column() != 0:
                    index = self.dialog.view.model().index(index.row(), 0, index.parent())
                self.dialog.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)
                self.dialog.view.expand(index)    

        if not self.datasource.tree:
            self.createNodes()
                
        self.datasource.applied = True

        return True    


    ## creates DOM datasource node
    # \param root root node 
    def __createDOMNodes(self, root):
        newDs = root.createElement(QString("datasource"))
        elem=newDs.toElement()
#        attributeMap = self.datasource.newDs.attributes()
        elem.setAttribute(QString("type"), QString(self.datasource.dataSourceType))
        if self.datasource.dataSourceName:
            elem.setAttribute(QString("name"), QString(self.datasource.dataSourceName))
        else:
            print "name not defined"
        if self.datasource.dataSourceType == 'CLIENT':
            record = root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.datasource.clientRecordName))
            elem.appendChild(record)            
        elif self.datasource.dataSourceType == 'TANGO':
            record = root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.datasource.tangoMemberName))
            elem.appendChild(record)            

            device = root.createElement(QString("device"))
            device.setAttribute(QString("name"), QString(self.datasource.tangoDeviceName))
            device.setAttribute(QString("member"), QString(self.datasource.tangoMemberType))
            if self.datasource.tangoHost:
                device.setAttribute(QString("hostname"), QString(self.datasource.tangoHost))
            if self.datasource.tangoPort:
                device.setAttribute(QString("port"), QString(self.datasource.tangoPort))
            if self.datasource.tangoEncoding:
                device.setAttribute(QString("encoding"), QString(self.datasource.tangoEncoding))
            elem.appendChild(device)            
            
        elif self.datasource.dataSourceType == 'DB':
            db = root.createElement(QString("database"))
            db.setAttribute(QString("dbtype"), QString(self.datasource.dbType))
            for par in self.datasource.dbParameters.keys():
                if par == 'Oracle DSN':
                    newText = root.createTextNode(QString(self.datasource.dbParameters[par]))
                    db.appendChild(newText)
                else:
                    db.setAttribute(QString(self.__idbmap[par]), QString(self.datasource.dbParameters[par]))
            elem.appendChild(db)            

            query = root.createElement(QString("query"))
            query.setAttribute(QString("format"), QString(self.datasource.dbDataFormat))
            if self.datasource.dbQuery:
                newText = root.createTextNode(QString(self.datasource.dbQuery))
                query.appendChild(newText)

            elem.appendChild(query)            

        if(self.datasource.doc):
            newDoc = root.createElement(QString("doc"))
            newText = root.createTextNode(QString(self.datasource.doc))
            newDoc.appendChild(newText)
            elem.appendChild(newDoc)
        return elem    
        

    ## creates datasource node
    # \param external True if it should be create on a local DOM root, i.e. in component tree
    # \returns created DOM node   
    def createNodes(self, external = False):        
        if external:
            root = QDomDocument()
        else:
            if not self.dialog.root or not self.dialog.node:
                self.createHeader()
            root = self.dialog.root 

        elem = self.__createDOMNodes(root)    

        if external and hasattr(self.dialog.root, "importNode"):
            rootDs = self.dialog.root.importNode(elem, True)
        else:
            rootDs = elem
        return rootDs
        


    ## updates the Node
    # \brief It sets node from the self.dialog variables
    def updateNode(self, index=QModelIndex()):
#        print "tree", self.datasource.tree
#        print "index", index.internalPointer()

        newDs = self.createNodes(self.datasource.tree)
        oldDs = self.dialog.node

        elem = oldDs.toElement()
        

        if hasattr(index,"parent"):
            parent = index.parent()
        else:
            parent = QModelIndex()

        self.dialog.node = self.dialog.node.parentNode()   
        if self.datasource.tree:
            if self.dialog.view is not None and self.dialog.view.model() is not None: 
                self.dialog.dts.replaceNode(oldDs, newDs, parent, self.dialog.view.model())
        else:
            self.dialog.node.replaceChild(newDs, oldDs)
        self.dialog.node = newDs

    ## reconnects save actions
    # \brief It reconnects the save action 
    def reconnectSaveAction(self):
        if self.datasource.externalSave:
            self.dialog.disconnect(self.dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                   self.datasource.externalSave)
            self.dialog.connect(self.dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                self.datasource.externalSave)
        if self.datasource.externalStore:
            self.dialog.disconnect(self.dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                   self.datasource.externalStore)
            self.dialog.connect(self.dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                self.datasource.externalStore)
        if self.datasource.externalClose:
            self.dialog.disconnect(self.dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                   self.datasource.externalClose)
            self.dialog.connect(self.dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                self.datasource.externalClose)
        if self.datasource.externalApply:
            self.dialog.disconnect(self.dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                   self.datasource.externalApply)
            self.dialog.connect(self.dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                self.datasource.externalApply)


    ## connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    def connectExternalActions(self, externalApply=None, externalSave=None,  
                               externalClose = None, externalStore=None):
        if externalSave and self.datasource.externalSave is None:
            self.dialog.connect(self.dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                externalSave)
            self.datasource.externalSave = externalSave
        if externalStore and self.datasource.externalStore is None:
            self.dialog.connect(self.dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                externalStore)
            self.datasource.externalStore = externalStore
        if externalClose and self.datasource.externalClose is None:
            self.dialog.connect(self.dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                externalClose)
            self.datasource.externalClose = externalClose
        if externalApply and self.datasource.externalApply is None:
            self.dialog.connect(self.dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                externalApply)
            self.datasource.externalApply = externalApply

                    
    ## creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        if hasattr(self.dialog,"view") and self.dialog.view:
            self.dialog.view.setModel(None)
        self.datasource.document = QDomDocument()
        ## defined in NodeDlg class
        self.dialog.root = self.datasource.document
        processing = self.dialog.root.createProcessingInstruction("xml", "version='1.0'") 
        self.dialog.root.appendChild(processing)

        definition = self.dialog.root.createElement(QString("definition"))
        self.dialog.root.appendChild(definition)
        self.dialog.node = self.dialog.root.createElement(QString("datasource"))
        definition.appendChild(self.dialog.node)            
        return self.dialog.node
            

    ## copies the datasource to the clipboard
    # \brief It copies the current datasource to the clipboard
    def copyToClipboard(self):
        dsNode = self.createNodes(True)
        doc = QDomDocument()
        child = doc.importNode(dsNode,True)
        doc.appendChild(child)
        text = unicode(doc.toString(0))
        clipboard= QApplication.clipboard()
        clipboard.setText(text)
        

    ## copies the datasource from the clipboard  to the current datasource dialog
    # \return status True on success
    def copyFromClipboard(self):
        clipboard= QApplication.clipboard()
        text=unicode(clipboard.text())
        self.datasource.document = QDomDocument()
        self.dialog.root = self.datasource.document
        if not self.datasource.document.setContent(self.datasource.repair(text)):
            raise ValueError, "could not parse XML"
        else:
            if self.dialog and hasattr(self.dialog,"root"):
                self.dialog.root = self.datasource.document 
                self.dialog.node = self.dialog.dts.getFirstElement(self.datasource.document, 
                                                                   "datasource")
        if not self.dialog.node:
            return
        self.setFromNode(self.dialog.node)

        return True





        

## dialog defining datasource
class CommonDataSource(object):
    
    ## constructor
    def __init__(self):
        

#        ## datasource dialog parent
#        self.parent = parent

        ## data source type
        self.dataSourceType = 'CLIENT'
        ## attribute doc
        self.doc = u''

        ## datasource dialog
        self.dialog = NodeDlg()

        ## datasource name
        self.dataSourceName = u''

        ## client record name
        self.clientRecordName = u''

        ## Tango device name
        self.tangoDeviceName = u''
        ## Tango member name
        self.tangoMemberName = u''
        ## Tango member name
        self.tangoMemberType = u''
        ## Tango host name
        self.tangoHost = u''
        ## Tango host name
        self.tangoPort = u''
        ## encoding for DevEncoded Tango types
        self.tangoEncoding = u''

        ## database type
        self.dbType = 'MYSQL'
        ## database format
        self.dbDataFormat = 'SCALAR'
        ## database query
        self.dbQuery = ""
        ## database parameters
        self.dbParameters = {}

        ## external save method
        self.externalSave = None
        ## external store method
        self.externalStore = None
        ## external close method
        self.externalClose = None
        ## external apply method
        self.externalApply = None

        ## applied flag
        self.applied = False

        ## datasource id
        self.ids = None

        
        ## if datasource in the component tree
        self.tree = False
        



    ## clears the datasource content
    # \brief It sets the datasource variables to default values
    def clear(self):
        self.dataSourceType = 'CLIENT'
        self.dataSourceName = ''
        self.doc = u''

        self.clientRecordName = u''

        self.tangoDeviceName = u''
        self.tangoMemberName = u''
        self.tangoMemberType = u''
        self.tangoHost = u''
        self.tangoPort = u''
        self.tangoEncoding = u''

        self.dbType = 'MYSQL'
        self.dbDataFormat = 'SCALAR'
        self.dbQuery = ""
        self.dbParameters = {}

#        if self.dialog:
#            self.dialog.dbParam = {}
        
        

    ## provides the state of the datasource dialog        
    # \returns state of the datasource in tuple
    def getState(self):
        dbParameters = copy.copy(self.dbParameters)

        state = (self.dataSourceType,
                 self.doc,
                 self.clientRecordName, 
                 self.tangoDeviceName,
                 self.tangoMemberName,
                 self.tangoMemberType,
                 self.tangoHost,
                 self.tangoPort,
                 self.tangoEncoding,
                 self.dbType,
                 self.dbDataFormat,
                 self.dbQuery,
                 dbParameters,
                 self.dataSourceName
                 )
        return state



    ## sets the state of the datasource dialog        
    # \brief note that ids, applied and tree are not in the state
    # \param state state datasource written in tuple 
    def setState(self, state):

        (self.dataSourceType,
         self.doc,
         self.clientRecordName, 
         self.tangoDeviceName,
         self.tangoMemberName,
         self.tangoMemberType,
         self.tangoHost,
         self.tangoPort,
         self.tangoEncoding,
         self.dbType,
         self.dbDataFormat,
         self.dbQuery,
         dbParameters,
         self.dataSourceName
         ) = state
        self.dbParameters = copy.copy(dbParameters)



## dialog defining datasource
class DataSource(CommonDataSource):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DataSource, self).__init__()


        ## dialog parent
        self.parent = parent

        ## datasource dialog
        self.dialog = CommonDataSourceDlg(self, parent)

        ## datasource methods
        self.__methods = DataSourceMethods(self.dialog, self)

        ## datasource directory
        self.directory = ""

        ## datasource file name
        self.name = None

        ## DOM document
        self.document = None
        ## saved XML
        self.savedXML = None
        

        
    ## creates dialog
    # \brief It creates dialog, its GUI , updates Nodes and Form
    def createDialog(self):
        self.dialog = CommonDataSourceDlg(self, self.parent)
        self.__methods.setDialog(self.dialog)
        self.createGUI()
        self.updateNode()
        self.updateForm()


    ## clears the datasource content
    # \brief It sets the datasource variables to default values
    def clear(self):
        CommonDataSource.clear(self)
        if self.dialog:
            self.dialog.dbParam = {}


    ## checks if not saved
    # \returns True if it is not saved     
    def isDirty(self):
        string = self.get()

            
        return False if string == self.savedXML else True


    ## provides the datasource in xml string
    # \returns xml string    
    def get(self, indent = 0):
        if hasattr(self.document,"toString"):
            return unicode(self.document.toString(indent))


    ## sets file name of the datasource and its directory
    # \param name name of the datasource
    # \param directory directory of the datasources   
    def setName(self, name, directory):
        self.name = unicode(name)
#        self.dialog.ui.nameLineEdit.setText(self.name)
        if directory:
            self.directory = unicode(directory)



    ## loads datasources from default file directory
    # \param fname optional file name
    def load(self, fname = None):
        if fname is None:
            if not self.name:
                filename = unicode(QFileDialog.getOpenFileName(
                        self.dialog,"Open File",self.directory,
                        "XML files (*.xml);;HTML files (*.html);;"
                        "SVG files (*.svg);;User Interface files (*.ui)"))
                fi = QFileInfo(filename)
                fname = str(fi.fileName())
                if fname[-4:] == '.xml':
                    self.name = fname[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]
                    else:
                        self.name = fname
            else:
                filename = os.path.join(self.directory, self.name + ".ds.xml")
        else:
            filename = fname
            if not self.name:
                fi = QFileInfo(filename)
                fname = str(fi.fileName())
                if fname[-4:] == '.xml':
                    self.name = fname[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]
                    else:
                        self.name = fname
        try:

            fh = QFile(filename)
            if  fh.open(QIODevice.ReadOnly):
                self.document = QDomDocument()
                self.root = self.document
#                if not self.document.setContent(self.repair(fh)):
                if not self.document.setContent(fh):
                    raise ValueError, "could not parse XML"

                ds = self.dialog.dts.getFirstElement(self.document, "datasource")
                if ds:
                    self.setFromNode(ds)
                self.savedXML = self.document.toString(0)
            else:
                QMessageBox.warning(self.dialog, "Cannot open the file", 
                                    "Cannot open the file: %s" % (filename))
            try:
                self.createGUI()

            except Exception, e:
                QMessageBox.warning(self.dialog, "dialog not created", 
                                    "Problems in creating a dialog %s :\n\n%s" %(self.name,unicode(e)))
                
        except (IOError, OSError, ValueError), e:
            error = "Failed to load: %s" % e
            print error
            QMessageBox.warning(self.dialog, "Saving problem", error )

        except Exception, e:
            QMessageBox.warning(self.dialog, "Saving problem", e )
            print e
        finally:                 
            if fh is not None:
                fh.close()
                return filename

    ## repairs xml datasources 
    # \param xml xml string
    # \returns repaired xml        
    def repair(self, xml):
        olddoc = QDomDocument()
        if not olddoc.setContent(xml):
            raise ValueError, "could not parse XML"

        definition = olddoc.firstChildElement(QString("definition"))           
        if definition and definition.nodeName() =="definition":
            ds  = definition.firstChildElement(QString("datasource"))
            if ds and ds.nodeName() =="datasource":
                return xml
        
        ds = self.dialog.dts.getFirstElement(olddoc, "datasource")           
        
        newdoc = QDomDocument()
        processing = newdoc.createProcessingInstruction("xml", "version='1.0'") 
        newdoc.appendChild(processing)

        definition = newdoc.createElement(QString("definition"))
        newdoc.appendChild(definition)

        newds = newdoc.importNode(ds,True)
        definition.appendChild(newds)            
        return newdoc.toString(0)

            
    ## sets datasources from xml string
    # \param xml xml string
    # \param new True if datasource is not saved
    def set(self, xml,new = False):
        self.document = QDomDocument()
        self.root = self.document
        if not self.document.setContent(self.repair(xml)):
            raise ValueError, "could not parse XML"
        else:
            if self.dialog and hasattr(self.dialog,"root"):
                self.dialog.root = self.document 

        ds = self.dialog.dts.getFirstElement(self.document, "datasource")           
        if ds:
            self.setFromNode(ds)
            if new:
                self.savedXML = ""
            else:
                self.savedXML = self.document.toString(0)
        try:    
            self.createGUI()
        except Exception, e:
            QMessageBox.warning(self, "dialog not created", 
                                "Problems in creating a dialog %s :\n\n%s" %(self.name,unicode(e)))
                

    ## accepts and save input text strings
    # \brief It copies the parameters and saves the dialog
    def save(self):

        error = None
        filename = os.path.join(self.directory, self.name + ".ds.xml") 
        print "saving in %s"% (filename)
        if filename:
            try:
                fh = QFile(filename)
                if not fh.open(QIODevice.WriteOnly):
                    raise IOError, unicode(fh.errorString())
                stream = QTextStream(fh)
                self.createNodes()

                xml = self.repair(self.document.toString(0))
                document = QDomDocument()
                document.setContent(xml)
                stream << document.toString(2)
            #                print self.document.toString(2)
                self.savedXML = document.toString(0)
            except (IOError, OSError, ValueError), e:
                error = "Failed to save: %s " % e \
                    + "Please try to use Save As command " \
                    + "or change the datasource directory"
                print error
                QMessageBox.warning(self.dialog, "Saving problem",  error )

            finally:
                if fh is not None:
                    fh.close()
        if not error:
            return True

    ## provides the datasource name with its path
    # \returns datasource name with its path 
    def getNewName(self):
        filename = unicode(
            QFileDialog.getSaveFileName(self.dialog,"Save DataSource As ...",self.directory,
                                        "XML files (*.xml);;HTML files (*.html);;"
                                        "SVG files (*.svg);;User Interface files (*.ui)"))
        print "saving in %s"% (filename)
        return filename





    ## gets the current view
    # \returns the current view  
    def _getview(self):
        if self.dialog and hasattr(self.dialog,"view"):
            return self.dialog.view

    ## sets the current view
    # \param view value to be set 
    def _setview(self, view):
        if self.dialog and hasattr(self.dialog,"view"):
            self.dialog.view = view

    ## attribute value       
    view = property(_getview, _setview)            



    ## gets the current root
    # \returns the current root  
    def _getroot(self):
        if self.dialog and hasattr(self.dialog,"root"):
            return self.dialog.root

    ## sets the current root
    # \param root value to be set 
    def _setroot(self, root):
        if self.dialog and hasattr(self.dialog,"root"):
            self.dialog.root = root

    ## attribute value       
    root = property(_getroot, _setroot)            






    ## shows dialog
    # \brief It adapts the dialog method
    def show(self):
        if hasattr(self,"datasource")  and self.dialog:
            if self.dialog:
                return self.dialog.show()


    ## clears the dialog
    # \brief clears the dialog
    def clearDialog(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.setDialog(None)

    ## updates the form
    # \brief abstract class
    def updateForm(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.updateForm()


    ## updates the node
    # \brief abstract class
    def updateNode(self, index=QModelIndex()):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.updateNode(index)

        

    ## creates GUI
    # \brief abstract class
    def createGUI(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.createGUI()

        
    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.setFromNode(node)

    ## creates datasource node
    # \param external True if it should be create on a local DOM root, i.e. in component tree
    # \returns created DOM node   
    def createNodes(self, external = False):        
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.createNodes(external)
        

    ## accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def apply(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.apply()


    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.treeMode(enable)

    ## connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    def connectExternalActions(self, externalApply=None, externalSave=None, 
                               externalClose=None,externalStore=None):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.connectExternalActions(
                externalApply, externalSave, externalClose, externalStore)

    ## reconnects save actions
    # \brief It reconnects the save action 
    def reconnectSaveAction(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.reconnectSaveAction()

        


    ## copies the datasource to the clipboard
    # \brief It copies the current datasource to the clipboard
    def copyToClipboard(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.copyToClipboard()
        

    ## copies the datasource from the clipboard  to the current datasource dialog
    # \return status True on success
    def copyFromClipboard(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.copyFromClipboard()


    ## creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.createHeader()

## dialog defining separate datasource
class DataSourceDlg(CommonDataSourceDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DataSourceDlg, self).__init__(None,parent)

        ## datasource data
        self.datasource = CommonDataSource()
        ## datasource methods
        self.__methods = DataSourceMethods(self, self.datasource)
        


            
    ## updates the form
    # \brief updates the form
    def updateForm(self):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.updateForm()


    ## clears the dialog
    # \brief clears the dialog
    def clearDialog(self):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.setDialog(None)


    ## updates the node
    # \brief updates the node 
    def updateNode(self, index=QModelIndex()):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.updateNode(index)
        

    ## creates GUI
    # \brief creates GUI
    def createGUI(self):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.createGUI()

        
    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.setFromNode(node)
        

    ## accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def apply(self):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.apply()


    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.treeMode(enable)

    ## connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action 
    # \param externalClose close action 
    # \param externalStore store action 
    def connectExternalActions(self, externalApply=None, externalSave=None, externalClose=None, externalStore=None):
        if hasattr(self,"_DataSourceDlg__methods")  and self.__methods:
            return self.__methods.connectExternalActions(externalApply, externalSave, externalClose, externalStore)


if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## data source form
    w = QWidget()
    w.show()
    ## the first datasource form
    form = DataSource(w)

    form.dataSourceType = 'CLIENT'
    form.clientRecordName = 'counter1'
    form.doc = 'The first client counter  '

    form.dataSourceType = 'TANGO'
    form.tangoDeviceName = 'p09/motor/exp.01'
    form.tangoMemberName = 'Position'
    form.tangoMemberType = 'attribute'
    form.tangoHost = 'hasso.desy.de'
    form.tangoPort = '10000'
    form.tangoEncoding = 'LIMA2D'

    form.dataSourceType = 'DB'
    form.dbType = 'PGSQL'
    form.dbDataFormat = 'SPECTRUM'
#    form.dbParameters = {'DB name':'tango', 'DB user':'tangouser'}

    form.createGUI()

    ## the second datasource form
    form2 = DataSourceDlg(w)
    form2.createGUI()
    form2.treeMode(True)

    form2.show()

    form.dialog.show()


    app.exec_()


#  LocalWords:  decryption
