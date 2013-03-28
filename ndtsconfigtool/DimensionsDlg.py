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
## \file DimensionsDlg.py
# Dimensions dialog class

import re
from PyQt4.QtCore import (SIGNAL, Qt, QVariant)
from PyQt4.QtGui import (QTableWidgetItem, QMessageBox, QDialog)
from ui.ui_dimensionsdlg import Ui_DimensionsDlg


## dialog defining a dimensions tag
class DimensionsDlg(QDialog):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DimensionsDlg, self).__init__(parent)

        ## dimensions rank
        self.rank = 0
        ## dimensions doc
        self.doc = u''
        ## dimensions lengths
        self.lengths = []

        ## user interface
        self.ui = Ui_DimensionsDlg()

        ## allowed subitems
        self.subItems = ["dim", "doc"]


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        try:
            if self.rank is not None and int(self.rank) >= 0 :
                self.rank = int(self.rank)
                for i, ln in enumerate(self.lengths):    
                    if ln:
                        self.lengths[i]=int(ln)
                        if self.lengths[i] < 1:
                            self.lengths[i] = None
                    else:        
                        self.lengths[i] = None
        except:
            self.rank = 1
            self.lengths = []
            
        if not self.lengths:
            self.lengths = []
            
        self.ui.setupUi(self)

        if self.doc :
            self.ui.docTextEdit.setText(self.doc)
        
        self.ui.rankSpinBox.setValue(self.rank)    

        self.connect(self.ui.dimTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.__tableItemChanged)

        self.ui.dimTableWidget.setSortingEnabled(False)
        self.populateLengths()
        self.ui.rankSpinBox.setFocus()

        self.connect(self.ui.rankSpinBox, SIGNAL("valueChanged(int)"), self.__valueChanged)

                
    ## takes a name of the current dim
    # \returns name of the current dim            
    def __currentTableDim(self):
        return self.ui.dimTableWidget.currentRow()


    ## changes the current value of the dim        
    # \brief It changes the current value of the dim 
    # and informs the user about wrong values
    def __tableItemChanged(self, item):
        row = self.__currentTableDim()
        
        if row not in range(len(self.lengths)):
            return
        column = self.ui.dimTableWidget.currentColumn()
        if column == 0:
            try:
                if item.text():
                    ln = int(item.text())
                    if ln < 1:
                        raise ValueError("Non-positive length value")
                    self.lengths[row] = ln
                else:
                    self.lengths[row] = None
            except:
                QMessageBox.warning(self, "Value Error", "Wrong value of the edited length")
                
        self.populateLengths()


    ## calls updateUi when the name text is changing
    # \param text the edited text   
    def __valueChanged(self, text):
        self.rank = int(self.ui.rankSpinBox.value())
        self.populateLengths(self.rank-1)


    ## fills in the dim table      
    # \param selectedDim selected dim    
    def populateLengths(self, selectedDim = None):
        selected = None
        self.ui.dimTableWidget.clear()
        self.ui.dimTableWidget.setRowCount(self.rank)
        
        while self.rank > len(self.lengths):
            self.lengths.append(None)
        
        headers = ["Length"]
        self.ui.dimTableWidget.setColumnCount(len(headers))
        self.ui.dimTableWidget.setHorizontalHeaderLabels(headers)	
        self.ui.dimTableWidget.setVerticalHeaderLabels( [unicode(l+1) for l in range(self.rank)] )	
        for row, ln in enumerate(self.lengths):
            if ln:
                item = QTableWidgetItem(unicode(ln))
            else:
                item = QTableWidgetItem("")
            item.setData(Qt.UserRole, QVariant(long(row)))
            if selectedDim is not None and selectedDim == row:
                selected = item
            self.ui.dimTableWidget.setItem(row, 0, item)
        self.ui.dimTableWidget.resizeColumnsToContents()
        self.ui.dimTableWidget.horizontalHeader().setStretchLastSection(True);
        if selected is not None:
            selected.setSelected(True)
            self.ui.dimTableWidget.setCurrentItem(selected)
            self.ui.dimTableWidget.editItem(selected)
            



    ## accepts input text strings
    # \brief It copies the dimensions name and type from lineEdit widgets and accept the dialog
    def accept(self):
        self.doc = unicode(self.ui.docTextEdit.toPlainText())
        while len(self.lengths) > self.rank:
            self.lengths.pop()
        QDialog.accept(self)

if __name__ == "__main__":
    import sys

    from PyQt4.QtGui import QApplication
    ## Qt application
    app = QApplication(sys.argv)
    ## dimensions form
    form = DimensionsDlg()
    form.rank = 2
    form.lengths = [25,27]
#    form.lengths = [None,3]
    form.doc = "Two dimentional array"
    form.createGUI()
    form.show()
    app.exec_()

    if form.result():
        if form.rank:
            print "Dimensions: rank = %s" % ( form.rank )
        if form.lengths:
            print "Lengths:"
            for row, ln in enumerate(form.lengths):
                print  " %s: %s " % (row+1, ln)
        if form.doc:
            print "Doc: \n%s" % form.doc
    
