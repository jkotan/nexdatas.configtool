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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_datasourcedlg
from PyQt4.QtXml import (QDomDocument, QDomNode)
from NodeDlg import NodeDlg 


## dialog defining datasources
class DataSourceDlg(NodeDlg, ui_datasourcedlg.Ui_DataSourceDlg):
    
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

        ## tango device name
        self.tangoDeviceName = u''
        ## tango member name
        self.tangoMemberName = u''
        ## tango member name
        self.tangoMemberType = u''
        ## tango host name
        self.tangoHost = u''
        ## tango host name
        self.tangoPort = u''

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




        ## parameter map for XMLdumper
        self.dbxml = {"DB name":"dbname",
                      "DB host":"host",
                      "DB port":"port",
                      "DB user":"user",
                      "DB password":"passwd",
                      "Mysql cnf":"mycnf",
                      "Oracle mode":"mode",
                      "Oracle DSN":"dsn"
                     } 

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
    
    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if enable:
            self.frame.hide()
        else:
            self.frame.show()
            
        
    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):


        self.setupUi(self)
        self.updateForm()

        self.resize(460, 440)

        self.connect(self.applyPushButton, SIGNAL("clicked()"), 
                     self.apply)
        self.connect(self.savePushButton, SIGNAL("clicked()"), 
                     self.save)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), 
                     self.reset)
        self.connect(self.closePushButton, SIGNAL("clicked()"), 
                     self.close)


        self.connect(self.dAddPushButton, SIGNAL("clicked()"), 
                     self.addParameter)
        self.connect(self.dRemovePushButton, SIGNAL("clicked()"), 
                     self.removeParameter)
        self.connect(self.dParameterTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.tableItemChanged)
        
        self.setFrames(self.dataSourceType)



    ## shows and hides frames according to typeComboBox
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_typeComboBox_currentIndexChanged(self, text):
        self.setFrames(text)


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

        

    ## calls updateUi when the name text is changing
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_dParamComboBox_currentIndexChanged(self, text):
        param = unicode(text)
        if param == 'DB password':
            QMessageBox.warning(self, "Unprotected password", "Please note that there is no support for any password protection")
            
        self.populateParameters(unicode(text))

    ## adds an parameter    
    #  \brief It runs the Parameter Dialog and fetches parameter name and value    
    def addParameter(self):
        name =  unicode(self.dParamComboBox.currentText())
        if name not in self._dbParam.keys():
            self._dbParam[name] = ""
        self.populateParameters(name)
    

    ## takes a name of the current parameter
    # \returns name of the current parameter
    def currentTableParameter(self):
        item = self.dParameterTableWidget.item(self.dParameterTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()

    ## removes an parameter    
    #  \brief It removes the current parameter asking before about it
    def removeParameter(self):
        param = self.currentTableParameter()
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
        param = self.currentTableParameter()
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


    ## loads datasources from default directory
    # \param fname optional file name
    def load(self, fname = None):
        if fname is None:
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

                ds = self.getFirstElement(self.document, "datasource")           
                self.setFromNode(ds)
            try:    
                self.createGUI()
            except Exception as e:
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


            

    def setFromNode(self, node=None):
        if node:
            self.node = node
        attributeMap = self.node.attributes()
        
        value = attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else ""
        
        if value == 'CLIENT':
            self.dataSourceType = value

            record = self.node.firstChildElement(QString("record"))           
            attributeMap = record.attributes()
            self.clientRecordName = attributeMap.namedItem("name").nodeValue() \
                if attributeMap.contains("name") else ""


        elif value == 'TANGO':
            self.dataSourceType = value

            record = self.node.firstChildElement(QString("record"))           
            attributeMap = record.attributes()
            self.tangoMemberName = attributeMap.namedItem("name").nodeValue() \
                if attributeMap.contains("name") else ""

            device = self.node.firstChildElement(QString("device"))           
            attributeMap = device.attributes()
            self.tangoDeviceName = attributeMap.namedItem("name").nodeValue() \
                if attributeMap.contains("name") else ""
            self.tangoMemberType = attributeMap.namedItem("member").nodeValue() \
                if attributeMap.contains("member") else "attribute"
            self.tangoHost = attributeMap.namedItem("hostname").nodeValue() \
                if attributeMap.contains("hostname") else ""
            self.tangoPort = attributeMap.namedItem("port").nodeValue() \
                if attributeMap.contains("port") else ""

                                    
        elif value == 'DB':
            self.dataSourceType = value
            
            database = self.node.firstChildElement(QString("database"))           
            attributeMap = database.attributes()

            for i in range(attributeMap.count()):
                name = attributeMap.item(i).nodeName()
                if name == 'dbtype':
                    self.dbType = attributeMap.item(i).nodeValue()
                elif name in self.dbmap:
                    self.dbParameters[self.dbmap[name]] = attributeMap.item(i).nodeValue()
                    self._dbParam[self.dbmap[name]] = attributeMap.item(i).nodeValue()

                    
            if not self.dbType:
                self.dbType = 'MYSQL'
                    
            text = self.getText(database)    
            self.dbParameters['Oracle DSN'] = unicode(text).strip() if text else ""
            self._dbParam['Oracle DSN'] = unicode(text).strip() if text else ""


            query = self.node.firstChildElement(QString("query"))           
            attributeMap = query.attributes()

            self.dbDataFormat = attributeMap.namedItem("format").nodeValue() \
                if attributeMap.contains("format") else "SCALAR"


            text = self.getText(query)    
            self.dbQuery = unicode(text).strip() if text else ""

        doc = self.node.firstChildElement(QString("doc"))           
        text = self.getText(doc)    
        self.doc = unicode(text).strip() if text else ""


    ## accepts and save input text strings
    # \brief It copies the parameters and saves the dialog
    def save(self):
        if not self.document or not self.node:
            self.createHeader()

        if self.apply():
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
                except (IOError, OSError, ValueError), e:
                    error = "Failed to save: %s" % e
                    print error
                    
                finally:
                    if fh is not None:
                        fh.close()


    ## rejects the changes
    # \brief It asks for the cancellation  and reject the changes
    def close(self):
        if QMessageBox.question(self, "Close datasource",
                                "Would you like to close the datasource?", 
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        self.revert()
        self.reject()


    def reset(self):
        self.revert()




   ## accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def apply(self):
        change  = False
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

        self.doc = unicode(self.docTextEdit.toPlainText())

        index = QModelIndex()
        if self.model:
            index = self.view.currentIndex()
            finalIndex = self.model.createIndex(index.row(),2,index.parent().internalPointer())

        if self.node  and self.root and self.node.isElement():
            self.updateNode(index)


            if self.model:
                self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index.parent(),index.parent())
                self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)

        

#        QDialog.accept(self)

        self.emit(SIGNAL("changed"))    
        return True    

    def createHeader(self):
            self.model = None
            self.document = QDomDocument()
            self.root = self.document
            processing = self.root.createProcessingInstruction("xml", 'version="1.0"') 
            self.root.appendChild(processing)
            
            definition = self.root.createElement(QString("definition"))
            self.root.appendChild(definition)
            self.node = self.root.createElement(QString("datasource"))
            definition.appendChild(self.node)            


            


    def createNodes(self):        
        if not self.root or not self.node:
            self.createHeader()

        newDs = self.root.createElement(QString("datasource"))
        elem=newDs.toElement()
#        attributeMap = self.newDs.attributes()
        elem.setAttribute(QString("type"), QString(self.dataSourceType))
        if self.dataSourceType == 'CLIENT':
            record = self.root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.clientRecordName))
            newDs.appendChild(record)            

        elif self.dataSourceType == 'TANGO':
            record = self.root.createElement(QString("record"))
            record.setAttribute(QString("name"), QString(self.tangoMemberName))
            newDs.appendChild(record)            

            device = self.root.createElement(QString("device"))
            device.setAttribute(QString("name"), QString(self.tangoDeviceName))
            device.setAttribute(QString("member"), QString(self.tangoMemberType))
            if self.tangoHost:
                device.setAttribute(QString("hostname"), QString(self.tangoHost))
            if self.tangoPort:
                device.setAttribute(QString("port"), QString(self.tangoPort))
            newDs.appendChild(device)            
            
        elif self.dataSourceType == 'DB':
            db = self.root.createElement(QString("database"))
            db.setAttribute(QString("dbtype"), QString(self.dbType))
            for par in self.dbParameters.keys():
                if par == 'Oracle DSN':
                    newText = self.root.createTextNode(QString(self.dbParameters[par]))
                    db.appendChild(newText)
                else:
                    db.setAttribute(QString(par), QString(self.dbParameters[par]))
            newDs.appendChild(db)            

            query = self.root.createElement(QString("query"))
            query.setAttribute(QString("format"), QString(self.dbDataFormat))
            if self.dbQuery:
                newText = self.root.createTextNode(QString(self.dbQuery))
                query.appendChild(newText)

            newDs.appendChild(query)            


        newDoc = self.root.createElement(QString("doc"))
        newText = self.root.createTextNode(QString(self.doc))
        newDoc.appendChild(newText)
        newDs.appendChild(newDoc)

        return newDs
        

    def updateNode(self,index=QModelIndex()):
        newDs = self.createNodes()
        oldDs = self.node

        self.node = self.node.parentNode()        
        if hasattr(index,"parent"):
            parent = index.parent()
        else:
            parent = QModelIndex()
        self.replaceNode(oldDs, newDs, parent)
        self.node = newDs


                    

    def revert(self):
        self.updateForm()


    def  showParameters(self):
    
        print "DataSource: %s " % (form.dataSourceType)
        
        if form.dataSourceType == 'CLIENT' :
            print "record name: %s " % (form.clientRecordName)


        if form.dataSourceType == 'TANGO' :
            print "device: %s, member: %s (%s) " % (form.tangoDeviceName,
                                                    form.tangoMemberName,
                                                    form.tangoMemberType,
                                                    )
            if form.tangoHost:
                print "host : %s " % form.tangoHost
            if form.tangoPort:
                print "port : %s " % form.tangoPort
        if form.dataSourceType == 'DB' :
            print "%s database, fetching %s data" % (form.dbType, form.dbDataFormat)
            for par in form.dbParameters.keys():
                print "%s = '%s'" % (par, form.dbParameters[par])
        if form.doc:
            print "Doc: \n%s" % form.doc


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

    form.dataSourceType = 'DB'
    form.dbType = 'PGSQL'
    form.dbDataFormat = 'SPECTRUM'
#    form.dbParameters = {'DB name':'tango', 'DB user':'tangouser'}

    form.createGUI()

    app.connect(form, SIGNAL("changed"), form.showParameters)
    form.show()
    app.exec_()


#  LocalWords:  decryption
