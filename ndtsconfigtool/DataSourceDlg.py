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
## \file DataSourceDlg.py
# Data Source dialog class

import re
from PyQt4.QtCore import (SIGNAL, QModelIndex, QString, Qt, QFileInfo, QFile, QIODevice, 
                          QTextStream, QVariant)
from PyQt4.QtGui import (QApplication, QFileDialog, QMessageBox, QTableWidgetItem)
from ui.ui_datasourcedlg import Ui_DataSourceDlg
from PyQt4.QtXml import (QDomDocument, QDomNode)
from NodeDlg import NodeDlg 
import copy
import gc

## dialog defining datasources
class DataSourceDlg(NodeDlg, Ui_DataSourceDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DataSourceDlg, self).__init__(parent)
        

        ## data source type
        self.dataSourceType = 'CLIENT'
        ## attribute doc
        self.doc = u''

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
        ## database parameters
        self._dbParam = {}

        self._externalSave = None
        self._externalApply = None

        self._applied = False

        ## parameter map for xml tags
        self.dbmap = {"dbname":"DB name",
                      "hostname":"DB host",
                      "port":"DB port",
                      "user":"DB user",
                      "passwd":"DB password",
                      "mycnf":"Mysql cnf",
                      "mode":"Oracle mode"
                     } 

        ## datasource id
        self.ids = None

        ## datasource directory
        self.directory = ""

        ## datasource name
        self.name = None

        ## DOM document
        self.document = None
        
        ## if datasource in the component tree
        self._tree = False
        
        ## allowed subitems
        self.subItems = ["record", "doc", "device", "database", "query", "door"]

        ## saved XML
        self.savedXML = None


    ## checks if not saved
    # \returns True if it is not saved     
    def isDirty(self):
        string = self.get()
        return False if string == self.savedXML else True


    ## clears the datasource content
    # \brief It sets the datasource variables to default values
    def clear(self):
        self.dataSourceType = 'CLIENT'
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
        self._dbParam = {}
        

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
                 dbParameters
                 )
#        print  "GET", str(state)
        return state



    ## sets the state of the datasource dialog        
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
         dbParameters
         ) = state
#        print "SET",  str(state)
        self.dbParameters = copy.copy(dbParameters)


    ## updates the datasource dialog
    # \brief It sets the form local variables
    def updateForm(self):    
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)

        if self.dataSourceType is not None:
            index = self.typeComboBox.findText(unicode(self.dataSourceType))
            if  index > -1 :
                self.typeComboBox.setCurrentIndex(index)
            else:
                self.dataSourceType = 'CLIENT'    
    
        if self.clientRecordName is not None:
            self.cRecNameLineEdit.setText(self.clientRecordName)

        if self.tangoDeviceName is not None:
            self.tDevNameLineEdit.setText(self.tangoDeviceName)
        if self.tangoMemberName is not None:
            self.tMemberNameLineEdit.setText(self.tangoMemberName)
        if self.tangoMemberType is not None:
            index = self.tMemberComboBox.findText(unicode(self.tangoMemberType))
            if  index > -1 :
                self.tMemberComboBox.setCurrentIndex(index)
            else:
                self.tangoMemberType = 'attribute'    
        if self.tangoHost is not None:
            self.tHostLineEdit.setText(self.tangoHost)
        if self.tangoPort is not None:
            self.tPortLineEdit.setText(self.tangoPort)
        if self.tangoEncoding is not None:
            self.tEncodingLineEdit.setText(self.tangoEncoding)



        if self.dbType  is not None:
            index = self.dTypeComboBox.findText(unicode(self.dbType))
            if  index > -1 :
                self.dTypeComboBox.setCurrentIndex(index)
            else:
                self.dbType = 'MYSQL'    
        if self.dbDataFormat is not None:
            index = self.dFormatComboBox.findText(unicode(self.dbDataFormat))
            if  index > -1 :
                self.dFormatComboBox.setCurrentIndex(index)
            else:
                self.dbDataFormat = 'INIT'    
        
        if self.dbQuery is not None:        
            self.dQueryLineEdit.setText(self.dbQuery)
                
        
        self._dbParam = {}
        for par in self.dbParameters.keys():
            index = self.dParamComboBox.findText(unicode(par))
            if  index < 0 :
                QMessageBox.warning(self, "Unregistered parameter", 
                                    "Unknown parameter %s = '%s' will be removed." 
                                    % (par, self.dbParameters[unicode(par)]) )
                self.dbParameters.pop(unicode(par))
            else:
                self._dbParam[unicode(par)]=self.dbParameters[(unicode(par))]
        self.populateParameters()
        self.setFrames(self.dataSourceType)
    
    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if enable:
            self.frame.hide()
            self._tree = True
        else:
            self._tree = False
            self.frame.show()
            
        
    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):


        self.setupUi(self)
        self.updateForm()

        self.resize(460, 440)

#        self.connect(self.applyPushButton, SIGNAL("clicked()"), self.apply)
#        self.connect(self.savePushButton, SIGNAL("clicked()"), self.save)

        self.connect(self.resetPushButton, SIGNAL("clicked()"), self.reset)
        self.connect(self.closePushButton, SIGNAL("clicked()"), self.close)


        self.connect(self.dAddPushButton, SIGNAL("clicked()"), 
                     self._addParameter)
        self.connect(self.dRemovePushButton, SIGNAL("clicked()"), 
                     self.removeParameter)
        self.connect(self.dParameterTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.tableItemChanged)
        

        self.connect(self.typeComboBox, SIGNAL("currentIndexChanged(QString)"), self._typeComboBox)
        self.connect(self.dParamComboBox, SIGNAL("currentIndexChanged(QString)"), self._dParamComboBox)
        self.connect(self.cRecNameLineEdit, SIGNAL("textEdited(QString)"), self._cRecNameLineEdit)
        self.connect(self.dQueryLineEdit, SIGNAL("textEdited(QString)"), self._dQueryLineEdit)
        self.connect(self.tDevNameLineEdit, SIGNAL("textEdited(QString)"), self._tDevNameLineEdit)
        self.connect(self.tMemberNameLineEdit, SIGNAL("textEdited(QString)"), self._tMemberNameLineEdit)


        self.setFrames(self.dataSourceType)


    ## connects external actions
    # \brief It connects the save action and stores the apply action
    def connectExternalActions(self, externalApply=None, externalSave=None):
        if externalSave and self._externalSave is None:
            self.connect(self.savePushButton, SIGNAL("clicked()"), 
                         externalSave)
            self._externalSave = externalSave
        if externalApply and self._externalApply is None:
            self.connect(self.applyPushButton, SIGNAL("clicked()"), 
                     externalApply)
            self._externalApply = externalApply


    ## shows and hides frames according to typeComboBox
    # \param text the edited text   
    def _typeComboBox(self, text):
        self.setFrames(text)
        self.updateUi(unicode(text))


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def _cRecNameLineEdit(self, text):
        combo = unicode(self.typeComboBox.currentText())
        self.updateUi(combo)


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def _dQueryLineEdit(self, text):
        combo = unicode(self.typeComboBox.currentText())
        self.updateUi(combo)



    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def _tDevNameLineEdit(self, text):
        combo = unicode(self.typeComboBox.currentText())
        self.updateUi(combo)


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def _tMemberNameLineEdit(self, text):
        combo = unicode(self.typeComboBox.currentText())
        self.updateUi(combo)


        
    ## updates group user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self, text):
        if text == 'CLIENT':
            enable = not self.cRecNameLineEdit.text().isEmpty()
            self.applyPushButton.setEnabled(enable)
            self.savePushButton.setEnabled(enable)
        elif text == 'DB':
            enable = not self.dQueryLineEdit.text().isEmpty()
            self.applyPushButton.setEnabled(enable)
            self.savePushButton.setEnabled(enable)
        elif text == 'TANGO':    
            enable = not self.tDevNameLineEdit.text().isEmpty() and \
                not self.tMemberNameLineEdit.text().isEmpty()
            self.applyPushButton.setEnabled(enable)
            self.savePushButton.setEnabled(enable)
        else:
            ## Additional non-supported frame
            enable = True
            self.applyPushButton.setEnabled(enable)
            self.savePushButton.setEnabled(enable)
        




    ## shows and hides frames according to typeComboBox
    # \param text the edited text   
    def setFrames(self,text):
        if text == 'CLIENT':
            self.clientFrame.show()
            self.dbFrame.hide()
            self.tangoFrame.hide()
        elif text == 'TANGO':
            self.clientFrame.hide()
            self.dbFrame.hide()
            self.tangoFrame.show()
        elif text == 'DB':
            self.clientFrame.hide()
            self.dbFrame.show()
            self.tangoFrame.hide()
            self.populateParameters()
            
        self.updateUi(text)


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def _dParamComboBox(self, text):
        param = unicode(text)
        if param == 'DB password':
            QMessageBox.warning(self, "Unprotected password", "Please note that there is no support for any password protection")
            
        self.populateParameters(unicode(text))

    ## adds an parameter    
    #  \brief It runs the Parameter Dialog and fetches parameter name and value    
    def _addParameter(self):
        name =  unicode(self.dParamComboBox.currentText())
        if name not in self._dbParam.keys():
            self._dbParam[name] = ""
        self.populateParameters(name)
    

    ## takes a name of the current parameter
    # \returns name of the current parameter
    def _currentTableParameter(self):
        item = self.dParameterTableWidget.item(self.dParameterTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()

    ## removes an parameter    
    #  \brief It removes the current parameter asking before about it
    def removeParameter(self):
        param = self._currentTableParameter()
        if param is None:
            return
        if QMessageBox.question(self, "Parameter - Remove",
                                "Remove parameter: %s = \'%s\'".encode() 
                                %  (param, self._dbParam[unicode(param)]),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        if unicode(param) in self._dbParam.keys():
            self._dbParam.pop(unicode(param))
            self.populateParameters()


    ## changes the current value of the parameter        
    # \brief It changes the current value of the parameter and informs the user that parameter names arenot editable
    def tableItemChanged(self, item):
        param = self._currentTableParameter()
        if unicode(param)  not in self._dbParam.keys():
            return
        column = self.dParameterTableWidget.currentColumn()
        if column == 1:
            self._dbParam[unicode(param)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Parameter name is not editable", "To change the parameter name, please remove the parameter and add the new one")
        self.populateParameters()


    ## fills in the paramter table      
    # \param selectedParameter selected parameter
    def populateParameters(self, selectedParameter = None):
        selected = None
        self.dParameterTableWidget.clear()
        self.dParameterTableWidget.setSortingEnabled(False)
        self.dParameterTableWidget.setRowCount(len(self._dbParam))
        headers = ["Name", "Value"]
        self.dParameterTableWidget.setColumnCount(len(headers))
        self.dParameterTableWidget.setHorizontalHeaderLabels(headers)	
        for row, name in enumerate(self._dbParam):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.dParameterTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self._dbParam[name])
            if selectedParameter is not None and selectedParameter == name:
                selected = item2
            self.dParameterTableWidget.setItem(row, 1, item2)
        self.dParameterTableWidget.setSortingEnabled(True)
        self.dParameterTableWidget.resizeColumnsToContents()
        self.dParameterTableWidget.horizontalHeader().setStretchLastSection(True);
        if selected is not None:
            selected.setSelected(True)
            self.dParameterTableWidget.setCurrentItem(selected)
            self.dParameterTableWidget.editItem(selected)


    ## sets name of the datasource and its directory
    # \param name name of the datasource
    # \param directory directory of the datasources   
    def setName(self, name, directory):
        self.name = unicode(name)
        if directory:
            self.directory = unicode(directory)
            


    ## loads datasources from default file directory
    # \param fname optional file name
    def load(self, fname = None):
        if fname is None:
            if not self.name:
                filename = unicode(QFileDialog.getOpenFileName(
                        self,"Open File",self.directory,
                        "XML files (*.xml);;HTML files (*.html);;"
                        "SVG files (*.svg);;User Interface files (*.ui)"))
                fi = QFileInfo(filename)
                fname = fi.fileName()
                if fname[-4:] == '.xml':
                    self. name = fname[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]
                    else:
                        self.name = fname
            else:
                filename = self.directory + "/" + self.name + ".ds.xml"
        else:
            filename = fname

        try:

            fh = QFile(filename)
            if  fh.open(QIODevice.ReadOnly):
                self.document = QDomDocument()
                self.root = self.document
                if not self.document.setContent(fh):
                    raise ValueError, "could not parse XML"

                ds = self._getFirstElement(self.document, "datasource")           
                if ds:
                    self.setFromNode(ds)
                self.savedXML = self.document.toString(0)
            try:    
                self.createGUI()
            except Exception, e:
                QMessageBox.warning(self, "dialog not created", 
                                    "Problems in creating a dialog %s :\n\n%s" %(self.name,str(e)))
                
        except (IOError, OSError, ValueError), e:
            error = "Failed to load: %s" % e
            print error
            
        except Exception, e:
            print e
        finally:                 
            if fh is not None:
                fh.close()
                return filename


            
    ## sets datasources from xml string
    # \param xml xml string
    def set(self, xml):
        self.document = QDomDocument()
        self.root = self.document
        if not self.document.setContent(xml):
            raise ValueError, "could not parse XML"

        ds = self._getFirstElement(self.document, "datasource")           
        if ds:
            self.setFromNode(ds)
            self.savedXML = self.document.toString(0)
        try:    
            self.createGUI()
        except Exception, e:
            QMessageBox.warning(self, "dialog not created", 
                                "Problems in creating a dialog %s :\n\n%s" %(self.name,str(e)))
                

            

    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg class
            self.node = node
        attributeMap = self.node.attributes()
        
        value = attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else ""
        
        if value == 'CLIENT':
            self.dataSourceType = unicode(value)

            record = self.node.firstChildElement(QString("record"))           
            attributeMap = record.attributes()
            self.clientRecordName = unicode(attributeMap.namedItem("name").nodeValue() \
                                                if attributeMap.contains("name") else "")



        elif value == 'TANGO':
            self.dataSourceType = unicode(value)

            record = self.node.firstChildElement(QString("record"))
            attributeMap = record.attributes()
            self.tangoMemberName = unicode(attributeMap.namedItem("name").nodeValue() \
                                               if attributeMap.contains("name") else "")

            device = self.node.firstChildElement(QString("device"))
            attributeMap = device.attributes()
            self.tangoDeviceName = unicode(attributeMap.namedItem("name").nodeValue() \
                                               if attributeMap.contains("name") else "")
            self.tangoMemberType = unicode(attributeMap.namedItem("member").nodeValue() \
                                               if attributeMap.contains("member") else "attribute")
            self.tangoHost = unicode(attributeMap.namedItem("hostname").nodeValue() \
                                         if attributeMap.contains("hostname") else "")
            self.tangoPort = unicode(attributeMap.namedItem("port").nodeValue() \
                                         if attributeMap.contains("port") else "")
            self.tangoEncoding = unicode(attributeMap.namedItem("encoding").nodeValue() \
                                         if attributeMap.contains("encoding") else "")

                                    
        elif value == 'DB':
            self.dataSourceType = unicode(value)
            
            database = self.node.firstChildElement(QString("database"))           
            attributeMap = database.attributes()

            for i in range(attributeMap.count()):
                name = unicode(attributeMap.item(i).nodeName())
                if name == 'dbtype':
                    self.dbType = unicode(attributeMap.item(i).nodeValue())
                elif name in self.dbmap:
                    self.dbParameters[self.dbmap[name]] = unicode(attributeMap.item(i).nodeValue())
                    self._dbParam[self.dbmap[name]] = unicode(attributeMap.item(i).nodeValue())

                    
            if not self.dbType:
                self.dbType = 'MYSQL'
                    
            text = unicode(self._getText(database))
            self.dbParameters['Oracle DSN'] = unicode(text).strip() if text else ""
            self._dbParam['Oracle DSN'] = unicode(text).strip() if text else ""


            query = self.node.firstChildElement(QString("query"))
            attributeMap = query.attributes()

            self.dbDataFormat = unicode(attributeMap.namedItem("format").nodeValue() \
                                            if attributeMap.contains("format") else "SCALAR")


            text = unicode(self._getText(query))
            self.dbQuery = unicode(text).strip() if text else ""


        doc = self.node.firstChildElement(QString("doc"))           
        text = self._getText(doc)    
        self.doc = unicode(text).strip() if text else ""


    ## provides the datasource in xml string
    # \returns xml string    
    def get(self, indent = 0):
        if hasattr(self.document,"toString"):
            return unicode(self.document.toString(indent))


    ## accepts and save input text strings
    # \brief It copies the parameters and saves the dialog
    def save(self):
        if self._applied:
            filename = self.directory + "/" + self.name + ".ds.xml"
            print "saving in %s"% (filename)
            error = None
            if filename:
                try:
                    fh = QFile(filename)
                    if not fh.open(QIODevice.WriteOnly):
                        raise IOError, unicode(fh.errorString())
                    stream = QTextStream(fh)
                    stream <<self.document.toString(2)
            #                print self.document.toString(2)
                    self.savedXML = self.document.toString(0)
                except (IOError, OSError, ValueError), e:
                    error = "Failed to save: %s" % e
                    print error
                finally:
                    if fh is not None:
                        fh.close()
        if not error:
            return True

    ## provides the datasource name with its path
    # \returns datasource name with its path 
    def getNewName(self):
        filename = unicode(
            QFileDialog.getSaveFileName(self,"Save DataSource As ...",self.directory,
                                        "XML files (*.xml);;HTML files (*.html);;"
                                        "SVG files (*.svg);;User Interface files (*.ui)"))
        print "saving in %s"% (filename)
        return filename



    ## rejects the changes
    # \brief It asks for the cancellation  and reject the changes
    def close(self):
        if QMessageBox.question(self, "Close datasource",
                                "Would you like to close the datasource?", 
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        self.updateForm()
        self.reject()


    ##  resets the form
    # \brief It reverts form variables to the last accepted ones    
    def reset(self):
        self.updateForm()




   ## accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def apply(self):
        gc.collect()
        print "A1"
        self._applied = False
        class CharacterError(Exception): pass
        sourceType = unicode(self.typeComboBox.currentText())

        if sourceType == 'CLIENT':
            recName = unicode(self.cRecNameLineEdit.text())

            if not recName:
                QMessageBox.warning(self, "Empty record name", 
                                    "Please define the record name")
                self.cRecNameLineEdit.setFocus()
                return
            self.clientRecordName = recName
        elif sourceType == 'TANGO':
            devName = unicode(self.tDevNameLineEdit.text())
            memName = unicode(self.tMemberNameLineEdit.text())
            if not devName: 
                QMessageBox.warning(self, "Empty device name", 
                                    "Please define the device name")
                self.tDevNameLineEdit.setFocus()
                return
            if not memName:
                QMessageBox.warning(self, "Empty member name", 
                                    "Please define the member name")
                self.tMemberNameLineEdit.setFocus()
                return
            self.tangoDeviceName = devName
            self.tangoMemberName = memName
            self.tangoMemberType = unicode(self.tMemberComboBox.currentText())
            self.tangoHost = unicode(self.tHostLineEdit.text())
            self.tangoPort = unicode(self.tPortLineEdit.text())
            self.tangoEncoding = unicode(self.tEncodingLineEdit.text())
                
        elif sourceType == 'DB':
            query = unicode(self.dQueryLineEdit.text())

            if not query:
                QMessageBox.warning(self, "Empty query", 
                                    "Please define the DB query")
                self.dQueryLineEdit.setFocus()
                return
            self.dbQuery = query
            self.dbType =  unicode(self.dTypeComboBox.currentText())
            self.dbDataFormat =  unicode(self.dFormatComboBox.currentText())

            self.dbParameters.clear()
            for par in self._dbParam.keys():
                self.dbParameters[par] = self._dbParam[par]


        self.dataSourceType = sourceType

        self.doc = unicode(self.docTextEdit.toPlainText()).strip()

        index = QModelIndex()
        if self.view and self.view.model():
            index = self.view.currentIndex()
            finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())

        print "AX1"
#        gc.collect()

        row = index.row()
        column = index.column()
        parent = index.parent()
        print "RCP", row, column, parent, parent.internalPointer() ,parent.internalPointer().node,parent.internalPointer().node.nodeName()

        if self.node  and self.root and self.node.isElement():

            self.updateNode(index)
            print "AX2"
#            gc.collect()

            if index.isValid():
                ind = self.view.model().index(row, column, parent)
#                ind = self.view.model().createIndex(row, column, parent.internalPointer().child(row))
                print "AX2b", ind.isValid()
                print "iRCP", ind.row(),ind.column(), ind.parent().internalPointer().node.nodeName(),ind.parent().parent().internalPointer().node.nodeName()

#                gc.collect()
                self.view.setCurrentIndex(ind)


            print "AX3"
        
            if self.view and self.view.model():
                self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index.parent(),index.parent())
                if  index.column() != 0:
                    index = self.view.model().index(index.row(), 0, index.parent())
                self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)

        print "TREE", self._tree
        if not self._tree:
            self.createNodes()
            print "CREATED"
#        else: 
#            self.createNodes(self._tree)
                
        self._applied = True
        print "AX"

        return True    


    ## creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        if self.view:
            self.view.setModel(None)
        self.document = QDomDocument()
        ## defined in NodeDlg class
        self.root = self.document
        processing = self.root.createProcessingInstruction("xml", 'version="1.0"') 
        self.root.appendChild(processing)

        definition = self.root.createElement(QString("definition"))
        self.root.appendChild(definition)
        self.node = self.root.createElement(QString("datasource"))
        definition.appendChild(self.node)            
        return self.node
            

    ## copies the datasource to the clipboard
    # \brief It copies the current datasource to the clipboard
    def copyToClipboard(self):
        dsNode = self.createNodes()
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
        self.document = QDomDocument()
        self.root = self.document
        if not self.document.setContent(text):
            raise ValueError, "could not parse XML"

        ds = self._getFirstElement(self.document, "datasource")           
        if not ds:
            return
        self.setFromNode(ds)
        return True


    ## creates datasource node
    # \param external True if it should be create on a local DOM root, i.e. in component tree
    # \returns created DOM node   
    def createNodes(self,external = False):        
        if external:
            root = QDomDocument()
        else:
            if not self.root or not self.node:
                self.createHeader()
            root = self.root 

        newDs = root.createElement(QString("datasource"))
        elem=newDs.toElement()
#        attributeMap = self.newDs.attributes()
        elem.setAttribute(QString("type"), QString(self.dataSourceType))
        if self.dataSourceType == 'CLIENT':
            record = root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.clientRecordName))
            elem.appendChild(record)            
        elif self.dataSourceType == 'TANGO':
            record = root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.tangoMemberName))
            elem.appendChild(record)            

            device = root.createElement(QString("device"))
            device.setAttribute(QString("name"), QString(self.tangoDeviceName))
            device.setAttribute(QString("member"), QString(self.tangoMemberType))
            if self.tangoHost:
                device.setAttribute(QString("hostname"), QString(self.tangoHost))
            if self.tangoPort:
                device.setAttribute(QString("port"), QString(self.tangoPort))
            if self.tangoEncoding:
                device.setAttribute(QString("encoding"), QString(self.tangoEncoding))
            elem.appendChild(device)            
            
        elif self.dataSourceType == 'DB':
            db = root.createElement(QString("database"))
            db.setAttribute(QString("dbtype"), QString(self.dbType))
            for par in self.dbParameters.keys():
                if par == 'Oracle DSN':
                    newText = root.createTextNode(QString(self.dbParameters[par]))
                    db.appendChild(newText)
                else:
                    db.setAttribute(QString(par), QString(self.dbParameters[par]))
            elem.appendChild(db)            

            query = root.createElement(QString("query"))
            query.setAttribute(QString("format"), QString(self.dbDataFormat))
            if self.dbQuery:
                newText = root.createTextNode(QString(self.dbQuery))
                query.appendChild(newText)

            elem.appendChild(query)            

        if(self.doc):
            newDoc = root.createElement(QString("doc"))
            newText = root.createTextNode(QString(self.doc))
            newDoc.appendChild(newText)
            elem.appendChild(newDoc)


        if external:
            rootDs = self.root.importNode(elem, True)
        else:
            rootDs = elem
        return rootDs
        


    ## updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self, index=QModelIndex()):
        newDs = self.createNodes(self._tree)
        oldDs = self.node


        if hasattr(index,"parent"):
            parent = index.parent()
        else:
            parent = QModelIndex()

        self.node = self.node.parentNode()   
        self._replaceNode(oldDs, newDs, parent)
        self.node = newDs

                    


if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## data source form
    form = DataSourceDlg()

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

    form.show()
    app.exec_()


#  LocalWords:  decryption
