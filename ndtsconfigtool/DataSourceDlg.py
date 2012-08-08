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


## dialog defining datasources
class DataSourceDlg(QDialog, ui_datasourcedlg.Ui_DataSourceDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DataSourceDlg, self).__init__(parent)
        

        ## data source type
        self.dataSourceType = 'CLIENT'
        ## strategy
        self.strategy = 'INIT'
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
        ## database parameters
        self.dbParameters = {}

        self.setupUi(self)
        self.resize(460, 440)

        self.clientFrame.show()
        self.dbFrame.hide()
        self.tangoFrame.hide()

        self.connect(self.dAddPushButton, SIGNAL("clicked()"), 
                     self.addParameter)
        self.connect(self.dRemovePushButton, SIGNAL("clicked()"), 
                     self.removeParameter)
        self.connect(self.dParameterTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.tableItemChanged)




    ## shows and hides frames according to typeComboBox
    # \param text the edited text   
    @pyqtSignature("QString")
    def on_typeComboBox_currentIndexChanged(self, text):
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
        if name not in self.dbParameters.keys():
            self.dbParameters[name] = ""
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
                                %  (param, self.dbParameters[unicode(param)]),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        if unicode(param) in self.dbParameters.keys():
            del self.dbParameters[unicode(param)]
            self.populateParameters()


    ## changes the current value of the parameter        
    # \brief It changes the current value of the parameter and informs the user that parameter names arenot editable
    def tableItemChanged(self, item):
        param = self.currentTableParameter()
        if unicode(param)  not in self.dbParameters.keys():
            return
        column = self.dParameterTableWidget.currentColumn()
        if column == 1:
            self.dbParameters[unicode(param)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Parameter name is not editable", "To change the parameter name, please remove the parameter and add the new one")
        self.populateParameters()


    ## fills in the paramter table      
    # \param selectedParameter selected parameter
    def populateParameters(self, selectedParameter = None):
        selected = None
        self.dParameterTableWidget.clear()
        self.dParameterTableWidget.setSortingEnabled(False)
        self.dParameterTableWidget.setRowCount(len(self.dbParameters))
        headers = ["Name", "Value"]
        self.dParameterTableWidget.setColumnCount(len(headers))
        self.dParameterTableWidget.setHorizontalHeaderLabels(headers)	
        for row, name in enumerate(self.dbParameters):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.dParameterTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self.dbParameters[name])
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
            





   ## accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def accept(self):
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
            self.dbType =  unicode(self.dTypeComboBox.currentText())
            self.dbDataFormat =  unicode(self.dFormatComboBox.currentText())

        self.dataSourceType = sourceType
        self.strategy = unicode(self.strategyComboBox.currentText())

        self.doc = unicode(self.docTextEdit.toPlainText())

        QDialog.accept(self)



if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## data source form
    form = DataSourceDlg()
    form.show()
    app.exec_()
    
    if form.result():
        print "DataSource: %s in the %s mode" % (form.dataSourceType, form.strategy )
        
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

#  LocalWords:  decryption
