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
        

        self.disconnect(self.ui.typeComboBox, SIGNAL("currentIndexChanged(QString)"), self.setFrames)
        self.disconnect(self.ui.cRecNameLineEdit, SIGNAL("textChanged(QString)"), self.__cRecNameLineEdit)
        self.disconnect(self.ui.tDevNameLineEdit, SIGNAL("textChanged(QString)"), self.__tDevNameLineEdit)
        self.disconnect(self.ui.tMemberNameLineEdit, SIGNAL("textChanged(QString)"), self.__tMemberNameLineEdit)
        self.disconnect(self.ui.dQueryLineEdit, SIGNAL("textChanged(QString)"), self.__dQueryLineEdit)
        self.disconnect(self.ui.dParamComboBox, SIGNAL("currentIndexChanged(QString)"), 
                     self.__dParamComboBox)
        self.disconnect(self.ui.dAddPushButton, SIGNAL("clicked()"), self.__addParameter)
        self.disconnect(self.ui.dRemovePushButton, SIGNAL("clicked()"), self.__removeParameter)
        self.disconnect(self.ui.dParameterTableWidget, SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.__tableItemChanged)



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
        self.__dialog = dialog

        ## datasource data
        self.__datasource = datasource

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
        self.__dialog = dialog

    ## rejects the changes
    # \brief It asks for the cancellation  and reject the changes
    def close(self):
        if QMessageBox.question(self.__dialog, "Close datasource",
                                "Would you like to close the datasource?", 
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return
        self.updateForm()
        self.__dialog.reject()


    ##  resets the form
    # \brief It reverts form variables to the last accepted ones    
    def reset(self):
        self.updateForm()


    ## updates the datasource self.__dialog
    # \brief It sets the form local variables
    def updateForm(self):    
        if not self.__dialog or not self.__datasource:
            raise ParameterError, "updateForm parameters not defined"
        if self.__datasource.doc is not None:
            self.__dialog.ui.docTextEdit.setText(self.__datasource.doc)
        if self.__datasource.dataSourceType is not None:
            index = self.__dialog.ui.typeComboBox.findText(unicode(self.__datasource.dataSourceType))
            if  index > -1 :
                self.__dialog.ui.typeComboBox.setCurrentIndex(index)
            else:
                self.__datasource.dataSourceType = 'CLIENT'    
    
        if self.__datasource.dataSourceName is not None:
            self.__dialog.ui.nameLineEdit.setText(self.__datasource.dataSourceName)

        if self.__datasource.clientRecordName is not None:
            self.__dialog.ui.cRecNameLineEdit.setText(self.__datasource.clientRecordName)

        if self.__datasource.tangoDeviceName is not None:
            self.__dialog.ui.tDevNameLineEdit.setText(self.__datasource.tangoDeviceName)
        if self.__datasource.tangoMemberName is not None:
            self.__dialog.ui.tMemberNameLineEdit.setText(self.__datasource.tangoMemberName)
        if self.__datasource.tangoMemberType is not None:
            index = self.__dialog.ui.tMemberComboBox.findText(unicode(self.__datasource.tangoMemberType))
            if  index > -1 :
                self.__dialog.ui.tMemberComboBox.setCurrentIndex(index)
            else:
                self.__datasource.tangoMemberType = 'attribute'    
        if self.__datasource.tangoHost is not None:
            self.__dialog.ui.tHostLineEdit.setText(self.__datasource.tangoHost)
        if self.__datasource.tangoPort is not None:
            self.__dialog.ui.tPortLineEdit.setText(self.__datasource.tangoPort)
        if self.__datasource.tangoEncoding is not None:
            self.__dialog.ui.tEncodingLineEdit.setText(self.__datasource.tangoEncoding)



        if self.__datasource.dbType  is not None:
            index = self.__dialog.ui.dTypeComboBox.findText(unicode(self.__datasource.dbType))
            if  index > -1 :
                self.__dialog.ui.dTypeComboBox.setCurrentIndex(index)
            else:
                self.__datasource.dbType = 'MYSQL'    
        if self.__datasource.dbDataFormat is not None:
            index = self.__dialog.ui.dFormatComboBox.findText(unicode(self.__datasource.dbDataFormat))
            if  index > -1 :
                self.__dialog.ui.dFormatComboBox.setCurrentIndex(index)
            else:
                self.__datasource.dbDataFormat = 'SCALAR'    
        
        if self.__datasource.dbQuery is not None:        
            self.__dialog.ui.dQueryLineEdit.setText(self.__datasource.dbQuery)
                
        
        self.__dialog.dbParam = {}
        for par in self.__datasource.dbParameters.keys():
            index = self.__dialog.ui.dParamComboBox.findText(unicode(par))
            if  index < 0 :
                QMessageBox.warning(self.__dialog, "Unregistered parameter", 
                                    "Unknown parameter %s = '%s' will be removed." 
                                    % (par, self.__datasource.dbParameters[unicode(par)]) )
                self.__datasource.dbParameters.pop(unicode(par))
            else:
                self.__dialog.dbParam[unicode(par)]=self.__datasource.dbParameters[(unicode(par))]
        self.__dialog.populateParameters()
        self.__dialog.setFrames(self.__datasource.dataSourceType)

    
    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if enable:
            self.__dialog.ui.closeSaveFrame.hide()
            self.__datasource.tree = True
        else:
            self.__datasource.tree = False
            self.__dialog.ui.closeSaveFrame.show()
            
        
    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        if self.__dialog and self.__dialog.ui and not hasattr(self.__dialog.ui,"resetPushButton"):
            self.__dialog.ui.setupUi(self.__dialog)

        self.updateForm()
        self.__dialog.resize(460, 440)

        if not self.__datasource.tree :
            self.__dialog.disconnect(self.__dialog.ui.resetPushButton, SIGNAL("clicked()"), self.reset)
            self.__dialog.connect(self.__dialog.ui.resetPushButton, SIGNAL("clicked()"), self.reset)
        else:
            self.__dialog.disconnect(self.__dialog.ui.resetPushButton, SIGNAL("clicked()"), self.__dialog.reset)
            self.__dialog.connect(self.__dialog.ui.resetPushButton, SIGNAL("clicked()"), self.__dialog.reset)
        self.__dialog.connectWidgets()
        self.__dialog.setFrames(self.__datasource.dataSourceType)

            

    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg class
            self.__dialog.node = node
            if self.__dialog:
                self.__dialog.node = node
        if not self.__dialog.node or not hasattr(self.__dialog.node,"attributes"):
            return
        attributeMap = self.__dialog.node.attributes()
        

        value = attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else ""
        if attributeMap.contains("name"):
            self.__datasource.dataSourceName = attributeMap.namedItem("name").nodeValue()
        
        if value == 'CLIENT':
            self.__datasource.dataSourceType = unicode(value)

            record = self.__dialog.node.firstChildElement(QString("record"))           
            if record.nodeName() != "record":
                QMessageBox.warning(self.__dialog, "Internal error", 
                                    "Missing <record> tag")
            else:
                attributeMap = record.attributes()
                self.__datasource.clientRecordName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                if attributeMap.contains("name") else "")
                


        elif value == 'TANGO':
            self.__datasource.dataSourceType = unicode(value)

            record = self.__dialog.node.firstChildElement(QString("record"))
            if record.nodeName() != "record":
                QMessageBox.warning(self.__dialog, "Internal error", 
                                    "Missing <record> tag")
            else:
                attributeMap = record.attributes()
                self.__datasource.tangoMemberName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                              if attributeMap.contains("name") else "")

            device = self.__dialog.node.firstChildElement(QString("device"))
            if device.nodeName() != "device":
                QMessageBox.warning(self.__dialog, "Internal error", 
                                    "Missing <device> tag")
            else:
                attributeMap = device.attributes()
                self.__datasource.tangoDeviceName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                              if attributeMap.contains("name") else "")
                self.__datasource.tangoMemberType = unicode(attributeMap.namedItem("member").nodeValue() \
                                                              if attributeMap.contains("member") else "attribute")
                self.__datasource.tangoHost = unicode(attributeMap.namedItem("hostname").nodeValue() \
                                                        if attributeMap.contains("hostname") else "")
                self.__datasource.tangoPort = unicode(attributeMap.namedItem("port").nodeValue() \
                                                        if attributeMap.contains("port") else "")
                self.__datasource.tangoEncoding = unicode(attributeMap.namedItem("encoding").nodeValue() \
                                                            if attributeMap.contains("encoding") else "")

                                    
        elif value == 'DB':
            self.__datasource.dataSourceType = unicode(value)
            database = self.__dialog.node.firstChildElement(QString("database"))           
            if database.nodeName() != "database":
                QMessageBox.warning(self.__dialog, "Internal error", 
                                    "Missing <database> tag")
            else:
                attributeMap = database.attributes()

                for i in range(attributeMap.count()):
                    name = unicode(attributeMap.item(i).nodeName())
                    if name == 'dbtype':
                        self.__datasource.dbType = unicode(attributeMap.item(i).nodeValue())
                    elif name in self.__dbmap:
                        self.__datasource.dbParameters[self.__dbmap[name]] = unicode(attributeMap.item(i).nodeValue())
                        self.__dialog.dbParam[self.__dbmap[name]] = unicode(attributeMap.item(i).nodeValue())
                        
            if not self.__datasource.dbType:
                self.__datasource.dbType = 'MYSQL'
            text = unicode(self.__dialog.dts.getText(database))
            self.__datasource.dbParameters['Oracle DSN'] = unicode(text).strip() if text else ""
            self.__dialog.dbParam['Oracle DSN'] = unicode(text).strip() if text else ""


            query = self.__dialog.node.firstChildElement(QString("query"))
            if query.nodeName() != "query":
                QMessageBox.warning(self.__dialog, "Internal error", 
                                    "Missing <query> tag")
            else:
                attributeMap = query.attributes()

                self.__datasource.dbDataFormat = unicode(attributeMap.namedItem("format").nodeValue() \
                                                           if attributeMap.contains("format") else "SCALAR")


            text = unicode(self.__dialog.dts.getText(query))
            self.__datasource.dbQuery = unicode(text).strip() if text else ""


        doc = self.__dialog.node.firstChildElement(QString("doc"))           
        text = self.__dialog.dts.getText(doc)    
        self.__datasource.doc = unicode(text).strip() if text else ""









    ## accepts input text strings
    # \brief It copies the parameters and accept the self.__dialog
    def apply(self):

        self.__datasource.applied = False
        sourceType = unicode(self.__dialog.ui.typeComboBox.currentText())
        self.__datasource.dataSourceName = unicode(self.__dialog.ui.nameLineEdit.text())

        if sourceType == 'CLIENT':
            recName = unicode(self.__dialog.ui.cRecNameLineEdit.text())

            if not recName:
                QMessageBox.warning(self.__dialog, "Empty record name", 
                                    "Please define the record name")
                self.__dialog.ui.cRecNameLineEdit.setFocus()
                return
            self.__datasource.clientRecordName = recName
        elif sourceType == 'TANGO':
            devName = unicode(self.__dialog.ui.tDevNameLineEdit.text())
            memName = unicode(self.__dialog.ui.tMemberNameLineEdit.text())
            if not devName: 
                QMessageBox.warning(self.__dialog, "Empty device name", 
                                    "Please define the device name")
                self.__dialog.ui.tDevNameLineEdit.setFocus()
                return
            if not memName:
                QMessageBox.warning(self.__dialog, "Empty member name", 
                                    "Please define the member name")
                self.__dialog.ui.tMemberNameLineEdit.setFocus()
                return
            self.__datasource.tangoDeviceName = devName
            self.__datasource.tangoMemberName = memName
            self.__datasource.tangoMemberType = unicode(self.__dialog.ui.tMemberComboBox.currentText())
            self.__datasource.tangoHost = unicode(self.__dialog.ui.tHostLineEdit.text())
            self.__datasource.tangoPort = unicode(self.__dialog.ui.tPortLineEdit.text())
            self.__datasource.tangoEncoding = unicode(self.__dialog.ui.tEncodingLineEdit.text())
                
        elif sourceType == 'DB':

            if not query:
                QMessageBox.warning(self, "Empty query", 
                                    "Please define the DB query")
                self.__datasource.dQueryLineEdit.setFocus()
                return
            self.__datasource.dbQuery = query
            self.__datasource.dbType =  unicode(self.__dialog.ui.dTypeComboBox.currentText())
            self.__datasource.dbDataFormat =  unicode(self.__dialog.ui.dFormatComboBox.currentText())

            self.__datasource.dbParameters.clear()
            for par in self.__dialog.dbParam.keys():
                self.__datasource.dbParameters[par] = self.__dialog.dbParam[par]


        self.__datasource.dataSourceType = sourceType

        self.__datasource.doc = unicode(self.__dialog.ui.docTextEdit.toPlainText()).strip()

        index = QModelIndex()
        if hasattr(self.__dialog,"view") and self.__dialog.view and self.__dialog.view.model():
            if hasattr(self.__dialog.view,"currentIndex"):
                index = self.__dialog.view.currentIndex()


                finalIndex = self.__dialog.view.model().createIndex(index.row(),2,index.parent().internalPointer())
                self.__dialog.view.expand(index)    


        row = index.row()
        column = index.column()
        parent = index.parent()

        if self.__dialog.root :
            self.updateNode(index)
                
            if index.isValid():
                index = self.__dialog.view.model().index(row, column, parent)
                self.__dialog.view.setCurrentIndex(index)
                self.__dialog.view.expand(index)
        
            if hasattr(self.__dialog,"view")  and self.__dialog.view and self.__dialog.view.model():
                self.__dialog.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index.parent(),index.parent())
                if  index.column() != 0:
                    index = self.__dialog.view.model().index(index.row(), 0, index.parent())
                self.__dialog.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)
                self.__dialog.view.expand(index)    

        if not self.__datasource.tree:
            self.createNodes()
                
        self.__datasource.applied = True

        return True    


    ## creates DOM datasource node
    # \param root root node 
    def __createDOMNodes(self, root):
        newDs = root.createElement(QString("datasource"))
        elem=newDs.toElement()
#        attributeMap = self.__datasource.newDs.attributes()
        elem.setAttribute(QString("type"), QString(self.__datasource.dataSourceType))
        if self.__datasource.dataSourceName:
            elem.setAttribute(QString("name"), QString(self.__datasource.dataSourceName))
        else:
            print "name not defined"
        if self.__datasource.dataSourceType == 'CLIENT':
            record = root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.__datasource.clientRecordName))
            elem.appendChild(record)            
        elif self.__datasource.dataSourceType == 'TANGO':
            record = root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.__datasource.tangoMemberName))
            elem.appendChild(record)            

            device = root.createElement(QString("device"))
            device.setAttribute(QString("name"), QString(self.__datasource.tangoDeviceName))
            device.setAttribute(QString("member"), QString(self.__datasource.tangoMemberType))
            if self.__datasource.tangoHost:
                device.setAttribute(QString("hostname"), QString(self.__datasource.tangoHost))
            if self.__datasource.tangoPort:
                device.setAttribute(QString("port"), QString(self.__datasource.tangoPort))
            if self.__datasource.tangoEncoding:
                device.setAttribute(QString("encoding"), QString(self.__datasource.tangoEncoding))
            elem.appendChild(device)            
            
        elif self.__datasource.dataSourceType == 'DB':
            db = root.createElement(QString("database"))
            db.setAttribute(QString("dbtype"), QString(self.__datasource.dbType))
            for par in self.__datasource.dbParameters.keys():
                if par == 'Oracle DSN':
                    newText = root.createTextNode(QString(self.__datasource.dbParameters[par]))
                    db.appendChild(newText)
                else:
                    db.setAttribute(QString(self.__idbmap[par]), QString(self.__datasource.dbParameters[par]))
            elem.appendChild(db)            

            query = root.createElement(QString("query"))
            query.setAttribute(QString("format"), QString(self.__datasource.dbDataFormat))
            if self.__datasource.dbQuery:
                newText = root.createTextNode(QString(self.__datasource.dbQuery))
                query.appendChild(newText)

            elem.appendChild(query)            

        if(self.__datasource.doc):
            newDoc = root.createElement(QString("doc"))
            newText = root.createTextNode(QString(self.__datasource.doc))
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
            if not self.__dialog.root or not self.__dialog.node:
                self.createHeader()
            root = self.__dialog.root 

        elem = self.__createDOMNodes(root)    

        if external and hasattr(self.__dialog.root, "importNode"):
            rootDs = self.__dialog.root.importNode(elem, True)
        else:
            rootDs = elem
        return rootDs
        


    ## updates the Node
    # \brief It sets node from the self.__dialog variables
    def updateNode(self, index=QModelIndex()):
#        print "tree", self.__datasource.tree
#        print "index", index.internalPointer()

        newDs = self.createNodes(self.__datasource.tree)
        oldDs = self.__dialog.node

        elem = oldDs.toElement()
        

        if hasattr(index, "parent"):
            parent = index.parent()
        else:
            parent = QModelIndex()
         

        self.__dialog.node = self.__dialog.node.parentNode()   
        if self.__datasource.tree:
            if self.__dialog.view is not None and self.__dialog.view.model() is not None: 
                self.__dialog.dts.replaceNode(oldDs, newDs, parent, self.__dialog.view.model())
        else:
            self.__dialog.node.replaceChild(newDs, oldDs)
        self.__dialog.node = newDs

    ## reconnects save actions
    # \brief It reconnects the save action 
    def reconnectSaveAction(self):
        if self.__datasource.externalSave:
            self.__dialog.disconnect(self.__dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                   self.__datasource.externalSave)
            self.__dialog.connect(self.__dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                self.__datasource.externalSave)
        if self.__datasource.externalStore:
            self.__dialog.disconnect(self.__dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                   self.__datasource.externalStore)
            self.__dialog.connect(self.__dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                self.__datasource.externalStore)
        if self.__datasource.externalClose:
            self.__dialog.disconnect(self.__dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                   self.__datasource.externalClose)
            self.__dialog.connect(self.__dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                self.__datasource.externalClose)
        if self.__datasource.externalApply:
            self.__dialog.disconnect(self.__dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                   self.__datasource.externalApply)
            self.__dialog.connect(self.__dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                self.__datasource.externalApply)


    ## connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    def connectExternalActions(self, externalApply=None, externalSave=None,  
                               externalClose = None, externalStore=None):
        if externalSave and self.__datasource.externalSave is None:
            self.__dialog.disconnect(self.__dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                externalSave)
            self.__dialog.connect(self.__dialog.ui.savePushButton, SIGNAL("clicked()"), 
                                externalSave)
            self.__datasource.externalSave = externalSave
        if externalStore and self.__datasource.externalStore is None:
            self.__dialog.disconnect(self.__dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                externalStore)
            self.__dialog.connect(self.__dialog.ui.storePushButton, SIGNAL("clicked()"), 
                                externalStore)
            self.__datasource.externalStore = externalStore
        if externalClose and self.__datasource.externalClose is None:
            self.__dialog.disconnect(self.__dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                externalClose)
            self.__dialog.connect(self.__dialog.ui.closePushButton, SIGNAL("clicked()"), 
                                externalClose)
            self.__datasource.externalClose = externalClose
        if externalApply and self.__datasource.externalApply is None:
            self.__dialog.disconnect(self.__dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                externalApply)
            self.__dialog.connect(self.__dialog.ui.applyPushButton, SIGNAL("clicked()"), 
                                externalApply)
            self.__datasource.externalApply = externalApply

                    
    ## creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        if hasattr(self.__dialog,"view") and self.__dialog.view:
            self.__dialog.view.setModel(None)
        self.__datasource.document = QDomDocument()
        ## defined in NodeDlg class
        self.__dialog.root = self.__datasource.document
        processing = self.__dialog.root.createProcessingInstruction("xml", "version='1.0'") 
        self.__dialog.root.appendChild(processing)

        definition = self.__dialog.root.createElement(QString("definition"))
        self.__dialog.root.appendChild(definition)
        self.__dialog.node = self.__dialog.root.createElement(QString("datasource"))
        definition.appendChild(self.__dialog.node)            
        return self.__dialog.node
            

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
        self.__datasource.document = QDomDocument()
        self.__dialog.root = self.__datasource.document
        if not self.__datasource.document.setContent(self.__datasource.repair(text)):
            raise ValueError, "could not parse XML"
        else:
            if self.__dialog and hasattr(self.__dialog,"root"):
                self.__dialog.root = self.__datasource.document 
                self.__dialog.node = self.__dialog.dts.getFirstElement(self.__datasource.document, 
                                                                   "datasource")
        if not self.__dialog.node:
            return
        self.setFromNode(self.__dialog.node)

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
        
        self.updateForm()
        self.updateNode()


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
