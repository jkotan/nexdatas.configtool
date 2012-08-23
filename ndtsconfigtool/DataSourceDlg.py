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

import XMLDumper
from xml.dom.minidom import parse




## dialog defining datasources
class DataSourceDlg(QDialog, ui_datasourcedlg.Ui_DataSourceDlg):
    
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

        ## datasource id
        self.directory = None
        ## datasource name
        self.name = None



    def setupForm(self):    
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
    



    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):


        self.setupUi(self)
        self.setupForm()

        self.resize(460, 440)

        self.connect(self.applyPushButton, SIGNAL("clicked()"), 
                     self.apply)
        self.connect(self.savePushButton, SIGNAL("clicked()"), 
                     self.save)
        self.connect(self.cancelPushButton, SIGNAL("clicked()"), 
                     self.cancel)


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
            doc = parse(filename)
            ds = doc.getElementsByTagName("datasource")[0]
            #            node = ds.documentElement        
            for (name, value) in ds.attributes.items():
                if name == 'type':  
                    if value == 'CLIENT':
                        self.dataSourceType = value
                        record = ds.getElementsByTagName("record")[0]
                        for (name, value) in record.attributes.items():
                            if name == 'name':
                                self.clientRecordName = value
                    if value == 'TANGO':
                        self.dataSourceType = value

                        try:
                            record = ds.getElementsByTagName("record")[0]
                            for (name, value) in record.attributes.items():
                                if name == 'name':
                                    self.tangoMemberName = value
                        except:
                            self.tangoMemberName = ""

                        try:
                            device = ds.getElementsByTagName("device")[0]
                            for (name, value) in device.attributes.items():
                                if name == 'name':
                                    self.tangoDeviceName = value
                                elif name == 'member':    
                                    self.tangoMemberType = value
                                elif name == 'hostname':    
                                    self.tangoHost = value
                                elif name == 'port':    
                                    self.tangoPort = value
                        except:
                            self.tangoDeviceName = ""
                            self.tangoMemberType = "attribute"
                            self.tangoHost = ""
                            self.tangoPort = ""
                                    
                    if value == 'DB':
                        self.dataSourceType = value

                        try:
                            database = ds.getElementsByTagName("database")[0]
                            for (name, value) in database.attributes.items():
                                if name == 'dbtype':
                                    self.dbType = value         
                                elif name in self.dbmap:
                                    self.dbParameters[self.dbmap[name]] = value
                                    self._dbParam[self.dbmap[name]] = value

                            dtxt = ""
                            for txt in database.childNodes:
                                if txt.nodeType == txt.TEXT_NODE:
                                    dtxt = dtxt + txt.data
                            self.dbParameters['Oracle DSN'] = dtxt.strip()
                            self._dbParam['Oracle DSN'] = dtxt.strip()
                        except:
                            self.dbType = 'MYSQL'
                                    

                        try:                                
                            query = ds.getElementsByTagName("query")[0]
                            for (name, value) in query.attributes.items():
                                if name == 'format':
                                    self.dbDataFormat = value         

                            qtxt = ""
                            for txt in query.childNodes:
                                if txt.nodeType == txt.TEXT_NODE:
                                    qtxt = qtxt + txt.data
                            self.dbQuery = qtxt.strip()
                        except:
                            self.dbDataFormat = 'SCALAR'
                            
            qtxt = ""
            try:  
                tdoc = doc.getElementsByTagName("doc")[0]
                for txt in tdoc.childNodes:
                    if txt.nodeType == txt.TEXT_NODE:
                        qtxt = qtxt + txt.data
            except:
                pass
            self.doc = qtxt.strip()
        except Exception as e:
            QMessageBox.warning(self, "XML not loaded", 
                                "Problems in loading the %s:\n\n%s" %(filename,str(e)))
        try:    
                    
            self.createGUI()
                
        except Exception as e:
            QMessageBox.warning(self, "dialog not created", 
                                "Problems in creating a dialog for %s:\n\n%s" %(filename,str(e)))

    ## accepts and save input text strings
    # \brief It copies the parameters and saves the dialog
    def save(self):
        if self.apply():
            filename = self.directory + "/" + self.name + ".ds.xml"
            print "saving in %s"% (filename)
            if filename:
                df = XMLDumper.XMLFile(filename)
                sr = XMLDumper.NDSource(df)
                if self.dataSourceType == 'CLIENT':
                    sr.initClient(self.clientRecordName);
                elif self.dataSourceType == 'TANGO':
                    args = {"device":self.tangoDeviceName, 
                            "memberType":self.tangoMemberType,
                            "recordName":self.tangoMemberName,
                            }
                    if self.tangoHost:
                        args["host"] = self.tangoHost
                    if self.tangoPort:
                        args["port"] = self.tangoPort 
                    sr.initTango(**args)
                elif self.dataSourceType == 'DB':
                    args = {"dbtype":self.dbType,
                            "format":self.dbDataFormat,
                            "query":self.dbQuery
                            }
                    
                    for name in self.dbParameters.keys():
                        if name in self.dbxml.keys():
                            args[self.dbxml[name]] =  self.dbParameters[name]

                    sr.initDBase(**args)
                if self.doc: 
                    sr.addDoc(self.doc)

                df.dump()    


    ## rejects the changes
    # \brief It asks for the cancellation  and reject the changes
    def cancel(self):
        if QMessageBox.question(self, "Cancel changes",
                                "Would you like to cancel?", 
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
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

#        QDialog.accept(self)

        self.emit(SIGNAL("changed"))    
        return True    

    def revert(self):
        self.setupForm()
        self.reject()


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
