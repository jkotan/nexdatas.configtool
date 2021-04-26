#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package nxsconfigtool nexdatas
# \file DataSources.py
# Data Sources for  datasource dialog class

""" widget for different types of datasources """

from PyQt5.QtCore import (Qt, QRegExp)
from PyQt5.QtGui import (QFontMetrics, QSyntaxHighlighter)
from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem)
from PyQt5.QtXml import (QDomDocument)
from PyQt5 import uic
import os
import sys

# from .ui.ui_clientdsdlg import Ui_ClientDsDlg
# from .ui.ui_dbdsdlg import Ui_DBDsDlg
# from .ui.ui_tangodsdlg import Ui_TangoDsDlg
# from .ui.ui_pyevaldsdlg import Ui_PyEvalDsDlg

from .DomTools import DomTools

_clientformclass, _clientbaseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "clientdsdlg.ui"))

_dbformclass, _dbbaseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "dbdsdlg.ui"))

_tangoformclass, _tangobaseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "tangodsdlg.ui"))

_pyevalformclass, _pyevalbaseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "pyevaldsdlg.ui"))

if sys.version_info > (3,):
    unicode = str


class FormatRule(object):
    __slots__ = 'expression', 'fmt', 'index'

    def __init__(self, expression, fmt, index=0):
        self.expression = expression
        self.fmt = fmt
        self.index = index


class SectionFormatRule(object):
    __slots__ = 'startExp', 'endExp', 'fmt', 'state', 'index'

    def __init__(self, startExp, endExp, fmt, state=-1, index=-1):
        self.startExp = startExp
        self.endExp = endExp
        self.fmt = fmt
        self.state = state
        self.index = index

    def reset(self):
        self.index = -1

    def nextStart(self, text, start=None):
        if start is not None:
            if start < self.index:
                return self.index
            self.index = self.startExp.indexIn(text, start)
        else:
            self.index = self.startExp.indexIn(text)
        return self.index


class PyEvalHighlighter(QSyntaxHighlighter):

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'exec', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
            'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'with',
            'while', 'yield', 'None', 'True', 'False', 'self'
        ]

        operators = [
            '\\^', '\\|', '\\&', '\\~', '>>', '<<', '\\%', '\\*\\*', '\\+=',
            '-=', '\\*=', '/=', '\\%=', '=', '==', '!=', '<', '<=', '>',
            '>=', '\\+', '-', '\\*', '/', '//', '\\.'
        ]

        self.rules = []

        self.rules.extend(
            [FormatRule(QRegExp(r'\b%s\b' % kw), Qt.blue)
             for kw in keywords])
        self.rules.extend(
            [FormatRule(QRegExp(r'%s' % op), Qt.darkGreen)
             for op in operators])
        self.rules.extend(
            [FormatRule(QRegExp(r'\bdef\b\s*(\w+)'), Qt.darkBlue, 1),
             FormatRule(QRegExp(r'\bclass\b\s*(\w+)'), Qt.darkBlue, 1)])
        # numeric
        self.rules.extend(
            [FormatRule(QRegExp(r'\b[+-]?[0-9]+[lL]?\b'), Qt.darkBlue),
             FormatRule(QRegExp(r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b'),
                        Qt.darkBlue),
             FormatRule(QRegExp(
                 r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b'),
                        Qt.darkBlue)])
        # datasources
        self.rules.append(
            FormatRule(
                QRegExp(r'\bds.[A-Za-z\(\)\.\$\_]+\b'), Qt.magenta))

        self.sectionrules = []

        # comments
        self.sectionrules.append(
            SectionFormatRule(QRegExp(r'#[^\n]*'), None, Qt.gray, 1))

        # multi-line strings
        self.sectionrules.extend(
            [SectionFormatRule(
                QRegExp(r'"""'), QRegExp(r'"""'), Qt.darkMagenta, 2),
             SectionFormatRule(
                QRegExp(r"'''"), QRegExp(r"'''"), Qt.darkMagenta, 3)])

        # strings
        self.sectionrules.extend(
            [SectionFormatRule(
                QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), None, Qt.darkMagenta, 4),
             SectionFormatRule(
                 QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), None, Qt.darkMagenta, 5)])

    def highlightBlock(self, text):

        for rule in self.rules:

            index = rule.expression.indexIn(text)
            while index >= 0:
                index = rule.expression.pos(rule.index)
                length = len(str(rule.expression.cap(rule.index)))
                self.setFormat(index, length, rule.fmt)
                index = rule.expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        for scrule in self.sectionrules:
            scrule.reset()

        state = self.previousBlockState()
        size = 0
        currentrule = None
        if self.previousBlockState() > 0:
            start = 0
        else:
            state = -1
            start = -1
            for scrule in self.sectionrules:
                rlstart = scrule.nextStart(text)
                if rlstart >= 0 and (start < 0 or rlstart < start):
                    start = rlstart
                    size = scrule.startExp.matchedLength()
                    state = scrule.state

        while start >= 0 and state > 0:
            currentrule = self.sectionrules[state - 1]
            if currentrule.endExp is not None:
                end = currentrule.endExp.indexIn(text, start + size)
                if end >= size:
                    length = end - start + size + \
                        currentrule.endExp.matchedLength()
                    self.setCurrentBlockState(0)
                else:
                    length = len(str(text)) - start + size
                    self.setCurrentBlockState(state)
            else:
                length = len(str(currentrule.startExp.cap(0)))
                self.setCurrentBlockState(0)

            self.setFormat(start, length, currentrule.fmt)
            state = -1
            newstart = -1
            for scrule in self.sectionrules:
                rlstart = scrule.nextStart(text, start + length)
                if rlstart >= 0 and (newstart < 0 or rlstart < newstart):
                    start = rlstart
                    newstart = rlstart
                    size = scrule.startExp.matchedLength()
                    state = scrule.state
            if state < 0:
                start = -1


# CLIENT dialog impementation
class ClientSource(object):
    # allowed subitems
    subItems = ["record", "doc"]
    # variables
    var = {
        # client record name
        "recordName": u''}

    # constructor
    # \param main datasource dialog
    def __init__(self, main):
        # widget class
        self.widgetClass = _clientformclass
        # widget
        self.ui = None
        #  main datasource dialog
        self.main = main

    # checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return bool(self.ui.cRecNameLineEdit.text())

    # calls updateUi when the name text is changing
    def __cRecNameLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

    # connects the dialog actions
    def connectWidgets(self):
        try:
            self.ui.cRecNameLineEdit.textChanged.disconnect(
                self.__cRecNameLineEdit)
        except Exception:
            pass
        self.ui.cRecNameLineEdit.textChanged.connect(
            self.__cRecNameLineEdit)
        # self.main.disconnect(
        #     self.ui.cRecNameLineEdit, SIGNAL("textChanged(str)"),
        #     self.__cRecNameLineEdit)
        # self.main.connect(
        #     self.ui.cRecNameLineEdit, SIGNAL("textChanged(str)"),
        #     self.__cRecNameLineEdit)

    # sets the tab order of subframe
    # \param first first widget from the parent dialog
    # \param last last widget from the parent dialog
    def setTabOrder(self, first, last):
        self.main.setTabOrder(first, self.ui.cRecNameLineEdit)
        self.main.setTabOrder(self.ui.cRecNameLineEdit, last)

    # updates datasource ui
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.var['CLIENT'].recordName is not None:
            self.ui.cRecNameLineEdit.setText(
                datasource.var['CLIENT'].recordName)

    # sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        record = self.main.node.firstChildElement(str("record"))
        if record.nodeName() != "record":
            QMessageBox.warning(self.main, "Internal error",
                                "Missing <record> tag")
        else:
            attributeMap = record.attributes()
            datasource.var['CLIENT'].recordName = unicode(
                attributeMap.namedItem("name").nodeValue()
                if attributeMap.contains("name") else "")

    # copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        recName = unicode(self.ui.cRecNameLineEdit.text())

        if not recName:
            QMessageBox.warning(self.main, "Empty record name",
                                "Please define the record name")
            self.ui.cRecNameLineEdit.setFocus()
            return
        datasource.var['CLIENT'].recordName = recName

    # creates datasource nodes
    # \param datasource class
    # \param root root node
    # \param elem datasource node
    def createNodes(self, datasource, root, elem):
        record = root.createElement(str("record"))
        record.setAttribute(
            str("name"), str(datasource.var['CLIENT'].recordName))
        elem.appendChild(record)


# DB dialog impementation
class DBSource(object):
    # allowed subitems
    subItems = ["query", "database", "doc"]
    # variables
    var = {
        # database type
        'dbtype': 'MYSQL',
        # database format
        'dataFormat': 'SCALAR',
        # database query
        'query': "",
        # database parameters
        'parameters': {}
    }

    # constructor
    # \param main datasource dialog
    def __init__(self, main):
        # widget class
        self.widgetClass = _dbformclass
        # widget
        self.ui = None
        # main datasource dialog
        self.main = main

        # database parameters
        self.dbParam = {}

        # parameter map for xml tags
        self.__dbmap = {
            "dbname": "DB name",
            "hostname": "DB host",
            "port": "DB port",
            "user": "DB user",
            "passwd": "DB password",
            "mycnf": "Mysql cnf",
            "mode": "Oracle mode"
        }
        self.__idbmap = dict(zip(self.__dbmap.values(), self.__dbmap.keys()))

    # clears widget parameters
    def clear(self):
        self.dbParam = {}

    # checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return bool(self.ui.dQueryLineEdit.text())

    # calls updateUi when the name text is changing
    def __dQueryLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

    # calls updateUi when the name text is changing
    # \param text the edited text
    def __dParamComboBox(self, text):
        param = unicode(text)
        if param == 'DB password':
            QMessageBox.warning(
                self, "Unprotected password",
                "Please note that there is no support for "
                "any password protection")

        self.populateParameters(unicode(text))

    # adds an parameter
    #  \brief It runs the Parameter Dialog and fetches parameter name
    #         and value
    def __addParameter(self):
        name = unicode(self.ui.dParamComboBox.currentText())
        if name not in self.dbParam.keys():
            self.dbParam[name] = ""
        self.populateParameters(name)

    # takes a name of the current parameter
    # \returns name of the current parameter
    def __currentTableParameter(self):
        item = self.ui.dParameterTableWidget.item(
            self.ui.dParameterTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole)

    # removes an parameter
    #  \brief It removes the current parameter asking before about it
    def __removeParameter(self):
        param = self.__currentTableParameter()
        if param is None:
            return
        if QMessageBox.question(self, "Parameter - Remove",
                                "Remove parameter: %s = \'%s\'".encode()
                                % (param, self.dbParam[unicode(param)]),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes) == QMessageBox.No:
            return
        if unicode(param) in self.dbParam.keys():
            self.dbParam.pop(unicode(param))
            self.populateParameters()

    # changes the current value of the parameter
    # \brief It changes the current value of the parameter and informs
    #        the user that parameter names arenot editable
    def __tableItemChanged(self, item):
        param = self.__currentTableParameter()
        if unicode(param) not in self.dbParam.keys():
            return
        column = self.ui.dParameterTableWidget.currentColumn()
        if column == 1:
            self.dbParam[unicode(param)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(
                self, "Parameter name is not editable",
                "To change the parameter name, "
                "please remove the parameter and add the new one")
        self.populateParameters()

    # fills in the paramter table
    # \param selectedParameter selected parameter
    def populateParameters(self, selectedParameter=None):
        selected = None
        self.ui.dParameterTableWidget.clear()
        self.ui.dParameterTableWidget.setSortingEnabled(False)
        self.ui.dParameterTableWidget.setRowCount(len(self.dbParam))
        headers = ["Name", "Value"]
        self.ui.dParameterTableWidget.setColumnCount(len(headers))
        self.ui.dParameterTableWidget.setHorizontalHeaderLabels(headers)
        for row, name in enumerate(self.dbParam):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, (name))
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

    # connects the dialog actions
    def connectWidgets(self):
        try:
            self.ui.dQueryLineEdit.textChanged.disconnect(
                self.__dQueryLineEdit)
        except Exception:
            pass
        try:
            self.ui.dParamComboBox.currentIndexChanged.disconnect(
                self.__dParamComboBox)
        except Exception:
            pass
        try:
            self.ui.dAddPushButton.clicked.disconnect(self.__addParameter)
        except Exception:
            pass
        try:
            self.ui.dRemovePushButton.clicked.disconnect(
                self.__removeParameter)
        except Exception:
            pass
        try:
            self.ui.dParameterTableWidget.itemChanged.disconnect(
                self.__tableItemChanged)
        except Exception:
            pass
        # self.main.disconnect(
        #     self.ui.dQueryLineEdit, SIGNAL("textChanged(str)"),
        #     self.__dQueryLineEdit)
        # self.main.disconnect(
        #     self.ui.dParamComboBox, SIGNAL("currentIndexChanged(str)"),
        #     self.__dParamComboBox)
        # self.main.disconnect(
        #     self.ui.dAddPushButton, SIGNAL("clicked()"), self.__addParameter)
        # self.main.disconnect(
        #     self.ui.dRemovePushButton, SIGNAL("clicked()"),
        #     self.__removeParameter)
        # self.main.disconnect(
        #     self.ui.dParameterTableWidget,
        #     SIGNAL("itemChanged(QTableWidgetItem*)"),
        #     self.__tableItemChanged)

        self.ui.dQueryLineEdit.textChanged.connect(self.__dQueryLineEdit)
        self.ui.dParamComboBox.currentIndexChanged.connect(
            self.__dParamComboBox)
        self.ui.dAddPushButton.clicked.connect(self.__addParameter)
        self.ui.dRemovePushButton.clicked.connect(self.__removeParameter)
        self.ui.dParameterTableWidget.itemChanged.connect(
            self.__tableItemChanged)

        # self.main.connect(
        #     self.ui.dQueryLineEdit,
        #     SIGNAL("textChanged(str)"), self.__dQueryLineEdit)
        # self.main.connect(
        #     self.ui.dParamComboBox, SIGNAL("currentIndexChanged(str)"),
        #     self.__dParamComboBox)
        # self.main.connect(
        #     self.ui.dAddPushButton, SIGNAL("clicked()"), self.__addParameter)
        # self.main.connect(
        #     self.ui.dRemovePushButton, SIGNAL("clicked()"),
        #     self.__removeParameter)
        # self.main.connect(
        #     self.ui.dParameterTableWidget,
        #     SIGNAL("itemChanged(QTableWidgetItem*)"),
        #     self.__tableItemChanged)

    # sets the tab order of subframe
    # \param first first widget from the parent dialog
    # \param last last widget from the parent dialog
    def setTabOrder(self, first, last):
        self.main.setTabOrder(first, self.ui.dTypeComboBox)
        self.main.setTabOrder(
            self.ui.dTypeComboBox, self.ui.dFormatComboBox)
        self.main.setTabOrder(
            self.ui.dFormatComboBox, self.ui.dQueryLineEdit)
        self.main.setTabOrder(
            self.ui.dQueryLineEdit, self.ui.dParamComboBox)
        self.main.setTabOrder(
            self.ui.dParamComboBox, self.ui.dAddPushButton)
        self.main.setTabOrder(
            self.ui.dAddPushButton, self.ui.dRemovePushButton)
        self.main.setTabOrder(
            self.ui.dRemovePushButton, self.ui.dParameterTableWidget)
        self.main.setTabOrder(self.ui.dParameterTableWidget, last)

    # updates datasource ui
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.var['DB'].dbtype is not None:
            index = self.ui.dTypeComboBox.findText(
                unicode(datasource.var['DB'].dbtype))
            if index > -1:
                self.ui.dTypeComboBox.setCurrentIndex(index)
            else:
                datasource.var['DB'].dbtype = 'MYSQL'
        if datasource.var['DB'].dataFormat is not None:
            index = self.ui.dFormatComboBox.findText(
                unicode(datasource.var['DB'].dataFormat))
            if index > -1:
                self.ui.dFormatComboBox.setCurrentIndex(index)
            else:
                datasource.var['DB'].dataFormat = 'SCALAR'

        if datasource.var['DB'].query is not None:
            self.ui.dQueryLineEdit.setText(datasource.var['DB'].query)

        self.dbParam = {}
        for par in datasource.var['DB'].parameters.keys():
            index = self.ui.dParamComboBox.findText(unicode(par))
            if index < 0:
                QMessageBox.warning(
                    self.main, "Unregistered parameter",
                    "Unknown parameter %s = '%s' will be removed."
                    % (par, datasource.var['DB'].parameters[unicode(par)]))
                datasource.var['DB'].parameters.pop(unicode(par))
            else:
                self.dbParam[unicode(par)] = datasource.var['DB'].parameters[
                    (unicode(par))]
        self.populateParameters()

    # sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        database = self.main.node.firstChildElement(str("database"))
        if database.nodeName() != "database":
            QMessageBox.warning(self.main, "Internal error",
                                "Missing <database> tag")
        else:
            attributeMap = database.attributes()

            for i in range(attributeMap.count()):
                name = unicode(attributeMap.item(i).nodeName())
                if name == 'dbtype':
                    datasource.var['DB'].dbtype = unicode(
                        attributeMap.item(i).nodeValue())
                elif name in self.__dbmap:
                    datasource.var['DB'].parameters[self.__dbmap[name]] = \
                        unicode(attributeMap.item(i).nodeValue())
                    self.dbParam[self.__dbmap[name]] = unicode(
                        attributeMap.item(i).nodeValue())

        if not datasource.var['DB'].dbtype:
            datasource.var['DB'].dbtype = 'MYSQL'
        text = unicode(DomTools.getText(database))
        datasource.var['DB'].parameters['Oracle DSN'] = unicode(text).strip() \
            if text else ""
        self.dbParam['Oracle DSN'] = unicode(text).strip() \
            if text else ""

        query = self.main.node.firstChildElement(str("query"))
        if query.nodeName() != "query":
            QMessageBox.warning(self.main, "Internal error",
                                "Missing <query> tag")
        else:
            attributeMap = query.attributes()

            datasource.var['DB'].dataFormat = unicode(
                attributeMap.namedItem("format").nodeValue()
                if attributeMap.contains("format") else "SCALAR")

        text = unicode(DomTools.getText(query))
        datasource.var['DB'].query = unicode(text).strip() if text else ""

    # copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        query = unicode(self.ui.dQueryLineEdit.text()).strip()
        if not query:
            QMessageBox.warning(self.main, "Empty query",
                                "Please define the DB query")
            self.ui.dQueryLineEdit.setFocus()
            return
        datasource.var['DB'].query = query
        datasource.var['DB'].dbtype = unicode(
            self.ui.dTypeComboBox.currentText())
        datasource.var['DB'].dataFormat = unicode(
            self.ui.dFormatComboBox.currentText())

        datasource.var['DB'].parameters.clear()
        for par in self.dbParam.keys():
            datasource.var['DB'].parameters[par] = self.dbParam[par]

    # creates datasource nodes
    # \param datasource class
    # \param root root node
    # \param elem datasource node
    def createNodes(self, datasource, root, elem):
        db = root.createElement(str("database"))
        db.setAttribute(
            str("dbtype"), str(datasource.var['DB'].dbtype))
        for par in datasource.var['DB'].parameters.keys():
            if par == 'Oracle DSN':
                newText = root.createTextNode(
                    str(datasource.var['DB'].parameters[par]))
                db.appendChild(newText)
            else:
                db.setAttribute(str(self.__idbmap[par]),
                                str(datasource.var['DB'].parameters[par]))
        elem.appendChild(db)

        query = root.createElement(str("query"))
        query.setAttribute(str("format"),
                           str(datasource.var['DB'].dataFormat))
        if datasource.var['DB'].query:
            newText = root.createTextNode(str(datasource.var['DB'].query))
            query.appendChild(newText)

        elem.appendChild(query)


# TANGO dialog impementation
class TangoSource(object):
    # allowed subitems
    subItems = ["device", "record", "doc"]

    # variables
    var = {
        # Tango device name
        'deviceName': u'',
        # Tango member name
        'memberName': u'',
        # Tango member name
        'memberType': u'',
        # Tango host name
        'host': u'',
        # Tango host name
        'port': u'',
        # encoding for DevEncoded Tango types
        'encoding': u'',
        # group for Tango DataSources
        'group': u''
    }

    # \param main datasource dialog
    def __init__(self, main):
        # widget class
        self.widgetClass = _tangoformclass
        # widget
        self.ui = None
        # main datasource dialog
        self.main = main

    # checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return bool(self.ui.tDevNameLineEdit.text()) and \
            bool(self.ui.tMemberNameLineEdit.text())

    # sets the tab order of subframe
    # \param first first widget from the parent dialog
    # \param last last widget from the parent dialog
    def setTabOrder(self, first, last):
        self.main.setTabOrder(first, self.ui.tDevNameLineEdit)
        self.main.setTabOrder(
            self.ui.tDevNameLineEdit, self.ui.tMemberComboBox)
        self.main.setTabOrder(
            self.ui.tMemberComboBox, self.ui.tMemberNameLineEdit)
        self.main.setTabOrder(
            self.ui.tMemberNameLineEdit, self.ui.tHostLineEdit)
        self.main.setTabOrder(
            self.ui.tHostLineEdit, self.ui.tPortLineEdit)
        self.main.setTabOrder(
            self.ui.tPortLineEdit, self.ui.tEncodingLineEdit)
        self.main.setTabOrder(
            self.ui.tEncodingLineEdit, self.ui.tGroupLineEdit)
        self.main.setTabOrder(self.ui.tGroupLineEdit, last)

    # updates datasource ui
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.var['TANGO'].deviceName is not None:
            self.ui.tDevNameLineEdit.setText(
                datasource.var['TANGO'].deviceName)
        if datasource.var['TANGO'].memberName is not None:
            self.ui.tMemberNameLineEdit.setText(
                datasource.var['TANGO'].memberName)
        if datasource.var['TANGO'].memberType is not None:
            index = self.ui.tMemberComboBox.findText(
                unicode(datasource.var['TANGO'].memberType))
            if index > -1:
                self.ui.tMemberComboBox.setCurrentIndex(index)
            else:
                datasource.var['TANGO'].memberType = 'attribute'
        if datasource.var['TANGO'].host is not None:
            self.ui.tHostLineEdit.setText(datasource.var['TANGO'].host)
        if datasource.var['TANGO'].port is not None:
            self.ui.tPortLineEdit.setText(datasource.var['TANGO'].port)
        if datasource.var['TANGO'].encoding is not None:
            self.ui.tEncodingLineEdit.setText(datasource.var['TANGO'].encoding)
        if datasource.var['TANGO'].group is not None:
            self.ui.tGroupLineEdit.setText(datasource.var['TANGO'].group)

    # calls updateUi when the name text is changing
    def __tDevNameLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

    # calls updateUi when the name text is changing
    def __tMemberNameLineEdit(self):
        combo = unicode(self.main.ui.typeComboBox.currentText())
        self.main.updateUi(combo)

    # connects the dialog actions
    def connectWidgets(self):
        try:
            self.ui.tDevNameLineEdit.textChanged.disconnect(
                self.__tDevNameLineEdit)
        except Exception:
            pass
        try:
            self.ui.tMemberNameLineEdit.textChanged.disconnect(
                self.__tMemberNameLineEdit)
        except Exception:
            pass
        # self.main.disconnect(
        #     self.ui.tDevNameLineEdit,
        #     SIGNAL("textChanged(str)"),
        #     self.__tDevNameLineEdit)
        # self.main.disconnect(
        #     self.ui.tMemberNameLineEdit, SIGNAL("textChanged(str)"),
        #     self.__tMemberNameLineEdit)
        self.ui.tDevNameLineEdit.textChanged.connect(
            self.__tDevNameLineEdit)
        self.ui.tMemberNameLineEdit.textChanged.connect(
            self.__tMemberNameLineEdit)
        # self.main.connect(
        #     self.ui.tDevNameLineEdit, SIGNAL("textChanged(str)"),
        #     self.__tDevNameLineEdit)
        # self.main.connect(
        #     self.ui.tMemberNameLineEdit, SIGNAL("textChanged(str)"),
        #     self.__tMemberNameLineEdit)

    # sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        record = self.main.node.firstChildElement(str("record"))
        if record.nodeName() != "record":
            QMessageBox.warning(self.main, "Internal error",
                                "Missing <record> tag")
        else:
            attributeMap = record.attributes()
            datasource.var['TANGO'].memberName = unicode(
                attributeMap.namedItem("name").nodeValue()
                if attributeMap.contains("name") else "")

        device = self.main.node.firstChildElement(str("device"))
        if device.nodeName() != "device":
            QMessageBox.warning(self.main, "Internal error",
                                "Missing <device> tag")
        else:
            attributeMap = device.attributes()
            datasource.var['TANGO'].deviceName = unicode(
                attributeMap.namedItem("name").nodeValue()
                if attributeMap.contains("name") else "")
            datasource.var['TANGO'].memberType = unicode(
                attributeMap.namedItem("member").nodeValue()
                if attributeMap.contains("member") else "attribute")
            datasource.var['TANGO'].host = unicode(
                attributeMap.namedItem("hostname").nodeValue()
                if attributeMap.contains("hostname") else "")
            datasource.var['TANGO'].port = unicode(
                attributeMap.namedItem("port").nodeValue()
                if attributeMap.contains("port") else "")
            datasource.var['TANGO'].encoding = unicode(
                attributeMap.namedItem("encoding").nodeValue()
                if attributeMap.contains("encoding") else "")
            datasource.var['TANGO'].group = unicode(
                attributeMap.namedItem("group").nodeValue()
                if attributeMap.contains("group") else "")

    # copies parameters from form to datasource instance
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
        datasource.var['TANGO'].deviceName = devName
        datasource.var['TANGO'].memberName = memName
        datasource.var['TANGO'].memberType = unicode(
            self.ui.tMemberComboBox.currentText())
        datasource.var['TANGO'].host = unicode(self.ui.tHostLineEdit.text())
        datasource.var['TANGO'].port = unicode(self.ui.tPortLineEdit.text())
        datasource.var['TANGO'].encoding = unicode(
            self.ui.tEncodingLineEdit.text())
        datasource.var['TANGO'].group = unicode(self.ui.tGroupLineEdit.text())

    # creates datasource nodes
    # \param datasource class
    # \param root root node
    # \param elem datasource node
    def createNodes(self, datasource, root, elem):
        record = root.createElement(str("record"))
        record.setAttribute(str("name"),
                            str(datasource.var['TANGO'].memberName))
        elem.appendChild(record)

        device = root.createElement(str("device"))
        device.setAttribute(str("name"),
                            str(datasource.var['TANGO'].deviceName))
        device.setAttribute(str("member"),
                            str(datasource.var['TANGO'].memberType))
        if datasource.var['TANGO'].host:
            device.setAttribute(str("hostname"),
                                str(datasource.var['TANGO'].host))
        if datasource.var['TANGO'].port:
            device.setAttribute(str("port"),
                                str(datasource.var['TANGO'].port))
        if datasource.var['TANGO'].encoding:
            device.setAttribute(str("encoding"),
                                str(datasource.var['TANGO'].encoding))
        if datasource.var['TANGO'].group:
            device.setAttribute(str("group"),
                                str(datasource.var['TANGO'].group))
        elem.appendChild(device)


# PYEVAL dialog impementation
class PyEvalSource(object):
    # allowed subitems
    subItems = ["datasource", "result", "doc"]

    # variables
    var = {
        # pyeval result variable
        'result': "ds.result",
        # pyeval datasource variables
        'input': "",
        # pyeval python script
        'script': "",
        # pyeval datasources
        'dataSources': {}
    }

    # \param main datasource dialog
    def __init__(self, main):
        # widget class
        self.widgetClass = _pyevalformclass
        # widget
        self.ui = None
        # main datasource dialog
        self.main = main

    # checks if widget button should be enable
    # \returns if widget button should be enable
    def isEnable(self):
        return True

    # connects the dialog actions
    def connectWidgets(self):
        self.ui.peInputLineEdit.setStyleSheet("color: magenta")
        self.ui.peResultLineEdit.setStyleSheet("color: magenta")
        font = self.ui.peScriptTextEdit.font()
        metrics = QFontMetrics(font)
        tabStop = 4
        if hasattr(self.ui.peScriptTextEdit, "setTabStopDistance"):
            self.ui.peScriptTextEdit.setTabStopDistance(
                tabStop * metrics.width(' '))
        else:
            self.ui.peScriptTextEdit.setTabStopWidth(
                tabStop * metrics.width(' '))
        self.highlighter = PyEvalHighlighter(self.ui.peScriptTextEdit)

    # sets the tab order of subframe
    # \param first first widget from the parent dialog
    # \param last last widget from the parent dialog
    def setTabOrder(self, first, last):
        self.main.setTabOrder(first, self.ui.peInputLineEdit)
        self.main.setTabOrder(
            self.ui.peInputLineEdit, self.ui.peScriptTextEdit)
        self.main.setTabOrder(
            self.ui.peScriptTextEdit, self.ui.peResultLineEdit)
        self.main.setTabOrder(self.ui.peResultLineEdit, last)

    # updates datasource ui
    # \param datasource class
    def updateForm(self, datasource):
        if datasource.var['PYEVAL'].result is not None:
            self.ui.peResultLineEdit.setText(datasource.var['PYEVAL'].result)
        if datasource.var['PYEVAL'].input is not None:
            self.ui.peInputLineEdit.setText(datasource.var['PYEVAL'].input)
        if datasource.var['PYEVAL'].script is not None:
            self.ui.peScriptTextEdit.setText(datasource.var['PYEVAL'].script)

    # sets the form from the DOM node
    # \param datasource class
    def setFromNode(self, datasource):
        res = self.main.node.firstChildElement(str("result"))
        text = DomTools.getText(res)
        while len(text) > 0 and text[0] == '\n':
            text = text[1:]
        datasource.var['PYEVAL'].script = unicode(text) if text else ""
        attributeMap = res.attributes()
        datasource.var['PYEVAL'].result = unicode(
            "ds." + attributeMap.namedItem("name").nodeValue()
            if attributeMap.contains("name") else "")

        ds = DomTools.getText(self.main.node)
        dslist = unicode(ds).strip().split() \
            if unicode(ds).strip() else []
        datasource.var['PYEVAL'].dataSources = {}
        child = self.main.node.firstChildElement(
            str("datasource"))
        while not child.isNull():
            if child.nodeName() == 'datasource':
                attributeMap = child.attributes()
                name = unicode(
                    attributeMap.namedItem("name").nodeValue()
                    if attributeMap.contains("name") else "")
                if name.strip():
                    dslist.append(name.strip())
                    doc = QDomDocument()
                    doc.appendChild(
                        doc.importNode(child, True))
                    datasource.var['PYEVAL'].dataSources[name] = unicode(
                        doc.toString(0))
                    child = child.nextSiblingElement("datasource")

        datasource.var['PYEVAL'].input = " ".join(
            "ds." + (d[13:] if (len(d) > 13 and d[:13] == "$datasources.")
                     else d) for d in dslist)

    # copies parameters from form to datasource instance
    # \param datasource class
    def fromForm(self, datasource):
        datasource.var['PYEVAL'].input = \
            unicode(self.ui.peInputLineEdit.text()).strip()
        datasource.var['PYEVAL'].result = \
            unicode(self.ui.peResultLineEdit.text()).strip()
        script = unicode(self.ui.peScriptTextEdit.toPlainText())
        if not script:
            QMessageBox.warning(self.main, "Empty script",
                                "Please define the PyEval script")
            if hasattr(self.ui, "dQueryLineEdit"):
                self.ui.dQueryLineEdit.setFocus()
            return
        script = script.replace('\t', '    ')
        datasource.var['PYEVAL'].script = script

    # creates datasource nodes
    # \param datasource class
    # \param root root node
    # \param elem datasource node
    def createNodes(self, datasource, root, elem):
        res = root.createElement(str("result"))
        rn = str(datasource.var['PYEVAL'].result).strip()
        if rn:
            res.setAttribute(
                str("name"),
                str(rn[3:] if (len(rn) > 3 and rn[:3] == 'ds.') else rn))
        if datasource.var['PYEVAL'].script:
            script = root.createTextNode(
                str(
                    datasource.var['PYEVAL'].script if (
                        len(datasource.var['PYEVAL'].script) > 0 and
                        datasource.var['PYEVAL'].script[0] == '\n') else (
                            "\n" + datasource.var['PYEVAL'].script))
                .replace("\t", "    "))
            res.appendChild(script)
        elem.appendChild(res)
        if datasource.var['PYEVAL'].input:
            dslist = unicode(datasource.var['PYEVAL'].input).split()
            newds = ""
            for d in dslist:
                name = d[3:] if (len(d) > 3 and d[:3] == 'ds.') else d
                if name in datasource.var['PYEVAL'].dataSources.keys():
                    document = QDomDocument()
                    if not document.setContent(
                            datasource.var['PYEVAL'].dataSources[name]):
                        raise ValueError("could not parse XML")
                    else:
                        if self.main and hasattr(self.main, "root"):

                            dsnode = DomTools.getFirstElement(
                                document, "datasource")
                            child = root.importNode(dsnode, True)
                            elem.appendChild(child)

                else:
                    newds = "\n ".join([newds, "$datasources." + name])

            newText = root.createTextNode(str(newds))
            elem.appendChild(newText)


if __name__ == "__main__":
    pass
