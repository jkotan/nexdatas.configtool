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
## \file DataSourceList.py
# Data source list class

""" datasource list widget """

import os 

from PyQt4.QtGui import QMessageBox

from .ui.ui_elementlist import Ui_ElementList
from .DataSource import DataSource
from .ElementList import ElementList
from .LabeledObject import LabeledObject


## dialog defining a group tag
class DataSourceList(ElementList):
    
    ## constructor
    # \param directory element directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(DataSourceList, self).__init__(parent)

        ## directory from which elements are loaded by default
        self.directory = directory
        
        ## group elements
        self.elements = {}

        ## actions
        self._actions = []

        ## user interface
        self.ui = Ui_ElementList()

        ## widget title
        self.title = "DataSources"
        ## element name
        self.name = "datasources"
        ## class name
        self.clName = "DataSource"
        ## extention
        self.extention = ".ds.xml"
        

    ## retrives element name from file name
    # \param fname filename
    # \returns element name        
    @classmethod
    def nameFromFile(cls, fname):
        if fname[-4:] == '.xml':
            name = fname[:-4]
            if name[-3:] == '.ds':
                name = name[:-3]
        else:
            name = fname
        return name    


    ## creates Element 
    # \param element name
    # \returns element instance
    def createElement(self, name):
        dlg = DataSource()
        dlg.directory = self.directory
        dlg.name = name
        dlg.createGUI()
        return dlg




    ## sets the elements
    # \param elements dictionary with the elements, i.e. name:xml
    # \param externalActions dictionary with external actions
    # \param new logical variableset to True if element is not saved
    def setList(self, elements, externalActions = None, new = False):
        actions = externalActions if externalActions else {}

        if not os.path.isdir(self.directory):
            try:
                if os.path.exists(os.path.join(os.getcwd(), self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(), self.name))
                else:
                    self.directory = os.getcwd()
            except:
                return
            
        ide = None    
        for elname in elements.keys():

            name =  "".join(
                x.replace('/','_').replace('\\','_').replace(':','_') \
                    for x in elname if (x.isalnum() or x in ["/","\\",":","_"]))
            dlg = DataSource()
            dlg.directory = self.directory
            dlg.name = name

            try:
                if str(elements[elname]).strip():
                    dlg.set(elements[elname], new)    
                else:
                    QMessageBox.warning(
                        self, "%s cannot be loaded" % self.clName,
                        "%s %s without content" % (self.clName, elname))
                    dlg.createGUI()
            except:
                QMessageBox.warning(
                    self, "%s cannot be loaded" % self.clName,
                    "%s %s cannot be loaded" % (self.clName, elname))
                dlg.createGUI()
                            
                
            dlg.dataSourceName = elname

            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(**actions)    
            
            el = LabeledObject(name, dlg)
            if new:
                el.savedName = ""

            ide = id(el)
            self.elements[ide] =  el
            if el.instance is not None:
                el.instance.id = el.id
                if new:
                    el.instance.applied =  True
            print name
        return ide    




if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = DataSourceList("../datasources")
#    form.elements={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.elements:
        print "Other datasources:"
        for k in form.elements.keys():
            print  " %s = '%s' " % (k, form.elements[k])
    
