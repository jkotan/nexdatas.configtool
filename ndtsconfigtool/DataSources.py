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
## \file DataSources.py
# Data Sources for  datasource dialog class

""" widget for different types of datasources """

from PyQt4.QtCore import (SIGNAL, QString, Qt, QVariant)
from PyQt4.QtGui import (QMessageBox, QTableWidgetItem)
from PyQt4.QtXml import (QDomDocument)

from .ui.ui_clientdsdlg import Ui_ClientDsDlg
from .ui.ui_dbdsdlg import Ui_DBDsDlg
from .ui.ui_tangodsdlg import Ui_TangoDsDlg
from .ui.ui_pyevaldsdlg import Ui_PyEvalDsDlg

from .DomTools import DomTools



## CLIENT dialog impementation
class ClientSource(object):
    ## allowed subitems
    subItems = ["record", "doc"]
    ## variables
    var = {
        ## client record name
        "clientRecordName":u''}

    ## constructor
    ## \param main datasource dialog
    def __init__(self, main):
        ## widget class
        self.widgetClass = Ui_ClientDsDlg
        ## widget
        self.ui = None
        ##  main datasource dialog
        self.main = main

    ## checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return not self.ui.cRecNameLineEdit.text().isEmpty()

    ## calls updateUi when the name text is changing
    def __cRecNameLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

    ## connects the dialog actions 
    def connectWidgets(self):
        self.main.disconnect(
            self.ui.cRecNameLineEdit, SIGNAL("textChanged(QString)"), 
            self.__cRecNameLineEdit)
        self.main.connect(
            self.ui.cRecNameLineEdit, SIGNAL("textChanged(QString)"), 
            self.__cRecNameLineEdit)


    ## updates datasource ui 
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.clientRecordName is not None:
            self.ui.cRecNameLineEdit.setText(datasource.clientRecordName)
        


    ## sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        record = self.main.node.firstChildElement(QString("record"))           
        if record.nodeName() != "record":
            QMessageBox.warning(self.main, "Internal error", 
                                    "Missing <record> tag")
        else:
            attributeMap = record.attributes()
            datasource.clientRecordName = unicode(
                attributeMap.namedItem("name").nodeValue() \
                    if attributeMap.contains("name") else "")
        

    ## copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        recName = unicode(self.ui.cRecNameLineEdit.text())

        if not recName:
            QMessageBox.warning(self.main, "Empty record name", 
                                "Please define the record name")
            self.ui.cRecNameLineEdit.setFocus()
            return
        datasource.clientRecordName = recName



    ## creates datasource nodes
    # \param datasource class
    # \param root root node 
    # \param elem datasource node 
    def createNodes(self, datasource, root, elem):
        record = root.createElement(QString("record"))
        record.setAttribute(
            QString("name"), QString(datasource.clientRecordName))
        elem.appendChild(record)            

        


## DB dialog impementation
class DBSource(object):
    ## allowed subitems
    subItems = ["query", "database", "doc"]
    ## variables
    var = {
       ## database type
        'dbType':'MYSQL',
        ## database format
        'dbDataFormat':'SCALAR',
        ## database query
        'dbQuery':"",
        ## database parameters
        'dbParameters':{}}

    ## constructor
    ## \param main datasource dialog
    def __init__(self, main):
        ## widget class
        self.widgetClass = Ui_DBDsDlg
        ## widget
        self.ui = None
        ## main datasource dialog
        self.main = main

        ## database parameters
        self.dbParam = {}

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
        
    ## clears widget parameters
    def clear(self):
        self.dbParam = {}
        

    ## checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return not self.ui.dQueryLineEdit.text().isEmpty()




    ## calls updateUi when the name text is changing
    def __dQueryLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

        

    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def __dParamComboBox(self, text):
        param = unicode(text)
        if param == 'DB password':
            QMessageBox.warning(
                self, "Unprotected password", 
                "Please note that there is no support for "\
                    "any password protection")
            
        self.populateParameters(unicode(text))


    ## adds an parameter    
    #  \brief It runs the Parameter Dialog and fetches parameter name 
    #         and value    
    def __addParameter(self):
        name =  unicode(self.ui.dParamComboBox.currentText())
        if name not in self.dbParam.keys():
            self.dbParam[name] = ""
        self.populateParameters(name)
    

    ## takes a name of the current parameter
    # \returns name of the current parameter
    def __currentTableParameter(self):
        item = self.ui.dParameterTableWidget.item(
            self.ui.dParameterTableWidget.currentRow(), 0)
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
    # \brief It changes the current value of the parameter and informs 
    #        the user that parameter names arenot editable
    def __tableItemChanged(self, item):
        param = self.__currentTableParameter()
        if unicode(param)  not in self.dbParam.keys():
            return
        column = self.ui.dParameterTableWidget.currentColumn()
        if column == 1:
            self.dbParam[unicode(param)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(
                self, "Parameter name is not editable", 
                "To change the parameter name, "\
                    "please remove the parameter and add the new one")
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
        self.ui.dParameterTableWidget.horizontalHeader()\
            .setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.dParameterTableWidget.setCurrentItem(selected)
            self.ui.dParameterTableWidget.editItem(selected)




    ## connects the dialog actions 
    def connectWidgets(self):
        self.main.disconnect(
            self.ui.dQueryLineEdit, SIGNAL("textChanged(QString)"), 
            self.__dQueryLineEdit)
        self.main.disconnect(
            self.ui.dParamComboBox, SIGNAL("currentIndexChanged(QString)"), 
            self.__dParamComboBox)
        self.main.disconnect(
            self.ui.dAddPushButton, SIGNAL("clicked()"), self.__addParameter)
        self.main.disconnect(
            self.ui.dRemovePushButton, SIGNAL("clicked()"), 
            self.__removeParameter)
        self.main.disconnect(
            self.ui.dParameterTableWidget, 
            SIGNAL("itemChanged(QTableWidgetItem*)"),
            self.__tableItemChanged)
        self.main.connect(
            self.ui.dQueryLineEdit, 
            SIGNAL("textChanged(QString)"), self.__dQueryLineEdit)
        self.main.connect(
            self.ui.dParamComboBox, SIGNAL("currentIndexChanged(QString)"), 
            self.__dParamComboBox)
        self.main.connect(
            self.ui.dAddPushButton, SIGNAL("clicked()"), self.__addParameter)
        self.main.connect(
            self.ui.dRemovePushButton, SIGNAL("clicked()"), 
            self.__removeParameter)
        self.main.connect(
            self.ui.dParameterTableWidget, 
            SIGNAL("itemChanged(QTableWidgetItem*)"),
            self.__tableItemChanged)


    ## updates datasource ui 
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.dbType  is not None:
            index = self.ui.dTypeComboBox.findText(
                unicode(datasource.dbType))
            if  index > -1 :
                self.ui.dTypeComboBox.setCurrentIndex(index)
            else:
                datasource.dbType = 'MYSQL'    
        if datasource.dbDataFormat is not None:
            index = self.ui.dFormatComboBox.findText(
                unicode(datasource.dbDataFormat))
            if  index > -1 :
                self.ui.dFormatComboBox.setCurrentIndex(index)
            else:
                datasource.dbDataFormat = 'SCALAR'    
        
        if datasource.dbQuery is not None:        
            self.ui.dQueryLineEdit.setText(datasource.dbQuery)
                
        
        self.dbParam = {}
        for par in datasource.dbParameters.keys():
            index = self.ui.dParamComboBox.findText(unicode(par))
            if  index < 0 :
                QMessageBox.warning(
                    self.main, "Unregistered parameter", 
                    "Unknown parameter %s = '%s' will be removed." 
                    % (par, datasource.dbParameters[unicode(par)]) )
                datasource.dbParameters.pop(unicode(par))
            else:
                self.dbParam[unicode(par)]=datasource.dbParameters[
                    (unicode(par))]
        self.populateParameters()


    ## sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        database = self.main.node.firstChildElement(QString("database"))
        if database.nodeName() != "database":
            QMessageBox.warning(self.main, "Internal error", 
                                "Missing <database> tag")
        else:
            attributeMap = database.attributes()

            for i in range(attributeMap.count()):
                name = unicode(attributeMap.item(i).nodeName())
                if name == 'dbtype':
                    datasource.dbType = unicode(
                        attributeMap.item(i).nodeValue())
                elif name in self.__dbmap:
                    datasource.dbParameters[self.__dbmap[name]] = \
                        unicode(attributeMap.item(i).nodeValue())
                    self.dbParam[self.__dbmap[name]] = unicode(
                        attributeMap.item(i).nodeValue())
                        
        if not datasource.dbType:
            datasource.dbType = 'MYSQL'
        text = unicode(DomTools.getText(database))
        datasource.dbParameters['Oracle DSN'] = unicode(text).strip() \
            if text else ""
        self.dbParam['Oracle DSN'] = unicode(text).strip() \
            if text else ""


        query = self.main.node.firstChildElement(QString("query"))
        if query.nodeName() != "query":
            QMessageBox.warning(self.main, "Internal error", 
                                    "Missing <query> tag")
        else:
            attributeMap = query.attributes()

            datasource.dbDataFormat = unicode(
                attributeMap.namedItem("format").nodeValue() \
                    if attributeMap.contains("format") else "SCALAR")


        text = unicode(DomTools.getText(query))
        datasource.dbQuery = unicode(text).strip() if text else ""


    ## copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        query = unicode(self.ui.dQueryLineEdit.text()).strip()
        if not query:
            QMessageBox.warning(self.main, "Empty query", 
                                "Please define the DB query")
            self.ui.dQueryLineEdit.setFocus()
            return
        datasource.dbQuery = query
        datasource.dbType =  unicode(self.ui.dTypeComboBox.currentText())
        datasource.dbDataFormat = unicode(self.ui.dFormatComboBox.currentText())

        datasource.dbParameters.clear()
        for par in self.dbParam.keys():
            datasource.dbParameters[par] = self.dbParam[par]


    ## creates datasource nodes
    # \param datasource class
    # \param root root node 
    # \param elem datasource node 
    def createNodes(self, datasource, root, elem):
        db = root.createElement(QString("database"))
        db.setAttribute(QString("dbtype"), QString(datasource.dbType))
        for par in datasource.dbParameters.keys():
            if par == 'Oracle DSN':
                newText = root.createTextNode(
                    QString(datasource.dbParameters[par]))
                db.appendChild(newText)
            else:
                db.setAttribute(QString(self.__idbmap[par]), 
                                QString(datasource.dbParameters[par]))
        elem.appendChild(db)            

        query = root.createElement(QString("query"))
        query.setAttribute(QString("format"), 
                           QString(datasource.dbDataFormat))
        if datasource.dbQuery:
            newText = root.createTextNode(QString(datasource.dbQuery))
            query.appendChild(newText)

        elem.appendChild(query)            


## TANGO dialog impementation
class TangoSource(object):
    ## allowed subitems
    subItems = ["device", "record", "doc"]

    ## variables
    var = {
        ## Tango device name
        'tangoDeviceName':u'',
        ## Tango member name
        'tangoMemberName':u'',
        ## Tango member name
        'tangoMemberType':u'',
        ## Tango host name
        'tangoHost':u'',
        ## Tango host name
        'tangoPort':u'',
        ## encoding for DevEncoded Tango types
        'tangoEncoding':u'',
        ## group for Tango DataSources
        'tangoGroup':u''
        }

    ## \param main datasource dialog
    def __init__(self, main):
        ## widget class
        self.widgetClass = Ui_TangoDsDlg
        ## widget
        self.ui = None
        ## main datasource dialog
        self.main = main


    ## checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return not self.ui.tDevNameLineEdit.text().isEmpty() and \
            not self.ui.tMemberNameLineEdit.text().isEmpty()



    ## updates datasource ui 
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.tangoDeviceName is not None:
            self.ui.tDevNameLineEdit.setText(datasource.tangoDeviceName)
        if datasource.tangoMemberName is not None:
            self.ui.tMemberNameLineEdit.setText(datasource.tangoMemberName)
        if datasource.tangoMemberType is not None:
            index = self.ui.tMemberComboBox.findText(
                unicode(datasource.tangoMemberType))
            if  index > -1 :
                self.ui.tMemberComboBox.setCurrentIndex(index)
            else:
                datasource.tangoMemberType = 'attribute'    
        if datasource.tangoHost is not None:
            self.ui.tHostLineEdit.setText(datasource.tangoHost)
        if datasource.tangoPort is not None:
            self.ui.tPortLineEdit.setText(datasource.tangoPort)
        if datasource.tangoEncoding is not None:
            self.ui.tEncodingLineEdit.setText(datasource.tangoEncoding)
        if datasource.tangoGroup is not None:
            self.ui.tGroupLineEdit.setText(datasource.tangoGroup)



    ## calls updateUi when the name text is changing
    def __tDevNameLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)


    ## calls updateUi when the name text is changing
    def __tMemberNameLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

    ## connects the dialog actions 
    def connectWidgets(self):
        self.main.disconnect(
            self.ui.tDevNameLineEdit, 
            SIGNAL("textChanged(QString)"), 
            self.__tDevNameLineEdit)
        self.main.disconnect(
            self.ui.tMemberNameLineEdit, SIGNAL("textChanged(QString)"), 
            self.__tMemberNameLineEdit)

        self.main.connect(
            self.ui.tDevNameLineEdit, SIGNAL("textChanged(QString)"), 
            self.__tDevNameLineEdit)
        self.main.connect(
            self.ui.tMemberNameLineEdit, SIGNAL("textChanged(QString)"), 
            self.__tMemberNameLineEdit)


    ## sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        record = self.main.node.firstChildElement(QString("record"))
        if record.nodeName() != "record":
            QMessageBox.warning(self.main, "Internal error", 
                                    "Missing <record> tag")
        else:
            attributeMap = record.attributes()
            datasource.tangoMemberName = unicode(
                attributeMap.namedItem("name").nodeValue() \
                    if attributeMap.contains("name") else "")

        device = self.main.node.firstChildElement(QString("device"))
        if device.nodeName() != "device":
            QMessageBox.warning(self.main, "Internal error", 
                                    "Missing <device> tag")
        else:
            attributeMap = device.attributes()
            datasource.tangoDeviceName = unicode(
                attributeMap.namedItem("name").nodeValue() \
                    if attributeMap.contains("name") else "")
            datasource.tangoMemberType = unicode(
                attributeMap.namedItem("member").nodeValue() \
                    if attributeMap.contains("member") else "attribute")
            datasource.tangoHost = unicode(
                attributeMap.namedItem("hostname").nodeValue() \
                    if attributeMap.contains("hostname") else "")
            datasource.tangoPort = unicode(
                attributeMap.namedItem("port").nodeValue() \
                    if attributeMap.contains("port") else "")
            datasource.tangoEncoding = unicode(
                attributeMap.namedItem("encoding").nodeValue() \
                    if attributeMap.contains("encoding") else "")
            datasource.tangoGroup = unicode(
                attributeMap.namedItem("group").nodeValue() \
                    if attributeMap.contains("group") else "")

    ## copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        devName = unicode(self.ui.tDevNameLineEdit.text())
        memName = unicode(self.ui.tMemberNameLineEdit.text())
        if not devName: 
            QMessageBox.warning(self.main, "Empty device name", 
                                "Please define the device name")
            self.ui.tDevNameLineEdit.setFocus()
            return
        if not memName:
            QMessageBox.warning(self.main, "Empty member name", 
                                "Please define the member name")
            self.ui.tMemberNameLineEdit.setFocus()
            return
        datasource.tangoDeviceName = devName
        datasource.tangoMemberName = memName
        datasource.tangoMemberType = unicode(
            self.ui.tMemberComboBox.currentText())
        datasource.tangoHost = unicode(self.ui.tHostLineEdit.text())
        datasource.tangoPort = unicode(self.ui.tPortLineEdit.text())
        datasource.tangoEncoding = unicode(self.ui.tEncodingLineEdit.text())
        datasource.tangoGroup = unicode(self.ui.tGroupLineEdit.text())


    ## creates datasource nodes
    # \param datasource class
    # \param root root node 
    # \param elem datasource node 
    def createNodes(self, datasource, root, elem):
        record = root.createElement(QString("record"))
        record.setAttribute(QString("name"), 
                            QString(datasource.tangoMemberName))
        elem.appendChild(record)            

        device = root.createElement(QString("device"))
        device.setAttribute(QString("name"), 
                            QString(datasource.tangoDeviceName))
        device.setAttribute(QString("member"), 
                            QString(datasource.tangoMemberType))
        if datasource.tangoHost:
            device.setAttribute(QString("hostname"), 
                                QString(datasource.tangoHost))
        if datasource.tangoPort:
            device.setAttribute(QString("port"), 
                                QString(datasource.tangoPort))
        if datasource.tangoEncoding:
            device.setAttribute(QString("encoding"), 
                                QString(datasource.tangoEncoding))
        if datasource.tangoGroup:
            device.setAttribute(QString("group"), 
                                QString(datasource.tangoGroup))
        elem.appendChild(device)            


## PYEVAL dialog impementation
class PyEvalSource(object):
    ## allowed subitems
    subItems = ["datasource", "result", "doc"]

    ## variables
    var = {
        ## pyeval result variable
        'peResult':"ds.result",
        ## pyeval datasource variables
        'peInput':"",
        ## pyeval python script
        'peScript':"",
        ## pyeval datasources
        'peDataSources':{}
        }

    ## \param main datasource dialog
    def __init__(self, main):
        ## widget class
        self.widgetClass = Ui_PyEvalDsDlg
        ## widget
        self.ui = None
        ## main datasource dialog
        self.main = main

    ## checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return True

    ## connects the dialog actions 
    def connectWidgets(self):
        pass



    ## updates datasource ui 
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.peResult is not None:
            self.ui.peResultLineEdit.setText(datasource.peResult)
        if datasource.peInput is not None:
            self.ui.peInputLineEdit.setText(datasource.peInput)
        if datasource.peScript is not None:
            self.ui.peScriptTextEdit.setText(datasource.peScript)



    ## sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        res = self.main.node.firstChildElement(QString("result"))           
        text = DomTools.getText(res)    
        while len(text)>0 and text[0] =='\n':
            text = text[1:]
        datasource.peScript = unicode(text) if text else ""
        attributeMap = res.attributes()
        datasource.peResult = unicode(
            "ds." + attributeMap.namedItem("name").nodeValue() \
                if attributeMap.contains("name") else "")

        ds = DomTools.getText(self.main.node)    
        dslist = unicode(ds).strip().split() \
            if unicode(ds).strip() else []
        datasource.peDataSources = {}
        child = self.main.node.firstChildElement(
            QString("datasource"))           
        while not child.isNull():
            if child.nodeName() == 'datasource':
                attributeMap = child.attributes()
                name = unicode(
                    attributeMap.namedItem("name").nodeValue() \
                        if attributeMap.contains("name") else "")
                if name.strip():
                    dslist.append(name.strip())
                    doc = QDomDocument()
                    doc.appendChild(
                        doc.importNode(child, True))
                    datasource.peDataSources[name] = unicode(doc.toString(0))
                    child = child.nextSiblingElement("datasource")    
                    
            
        datasource.peInput = " ".join(
            "ds."+ (d[13:] if (len(d)> 13 and d[:13] =="$datasources.") 
                    else d) for d in dslist)


    ## copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        datasource.peInput = unicode(self.ui.peInputLineEdit.text()).strip()
        datasource.peResult = unicode(self.ui.peResultLineEdit.text()).strip()
        script = unicode(self.ui.peScriptTextEdit.toPlainText())
        if not script:
            QMessageBox.warning(self.main, "Empty script", 
                                "Please define the PyEval script")
            self.ui.dQueryLineEdit.setFocus()
            return 
        datasource.peScript = script



    ## creates datasource nodes
    # \param datasource class
    # \param root root node 
    # \param elem datasource node 
    def createNodes(self, datasource, root, elem):
        res = root.createElement(QString("result"))
        rn = str(datasource.peResult).strip()
        if rn:
            res.setAttribute(
                QString("name"), 
                QString(rn[3:] if (len(rn) > 3 and rn[:3] == 'ds.' ) else rn))
        if datasource.peScript:
            script = root.createTextNode(
                QString(
                    datasource.peScript if (
                        len(datasource.peScript)>0 and \
                            datasource.peScript[0] == '\n') else (
                        "\n"+ datasource.peScript)))
            res.appendChild(script)
        elem.appendChild(res)            
        if datasource.peInput:
            dslist = unicode(datasource.peInput).split()
            newds = "" 
            for d in dslist:
                name = d[3:] if (len(d) > 3 and d[:3] == 'ds.' ) else d
                if name in datasource.peDataSources.keys():
                    document = QDomDocument() 
                    if not document.setContent(datasource.peDataSources[name]):
                        raise ValueError, "could not parse XML"  
                    else:
                        if self.main and hasattr(self.main,"root"):

                            dsnode = DomTools.getFirstElement(
                                document, "datasource")
                            child = root.importNode(dsnode, True)
                            elem.appendChild(child)

                else :
                    newds = "\n ".join([newds,"$datasources." + name])
                
            newText = root.createTextNode(QString(newds))
            elem.appendChild(newText)






if __name__ == "__main__":
    pass
