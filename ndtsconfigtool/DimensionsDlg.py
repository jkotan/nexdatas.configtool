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
## \file DimensionsDlg.py
# Dimensions dialog class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui.ui_dimensionsdlg import Ui_DimensionsDlg

from NodeDlg import NodeDlg 

## dialog defining a dimensions tag
class DimensionsDlg(NodeDlg, Ui_DimensionsDlg):
    
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
            
        self.setupUi(self)

        if self.doc :
            self.docTextEdit.setText(self.doc)
        
        self.rankSpinBox.setValue(self.rank)    

        self.connect(self.dimTableWidget, 
                     SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self.tableItemChanged)

        self.dimTableWidget.setSortingEnabled(False)
        self.populateLengths()
        self.rankSpinBox.setFocus()
                
    ## takes a name of the current dim
    # \returns name of the current dim            
    def currentTableDim(self):
        return self.dimTableWidget.currentRow()


    ## changes the current value of the dim        
    # \brief It changes the current value of the dim 
    # and informs the user about wrong values
    def tableItemChanged(self, item):
        row = self.currentTableDim()
        
        if row not in range(len(self.lengths)):
            return
        column = self.dimTableWidget.currentColumn()
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
    @pyqtSignature("int")
    def on_rankSpinBox_valueChanged(self, text):
        self.rank = int(self.rankSpinBox.value())
        self.populateLengths(self.rank-1)


    ## fills in the dim table      
    # \param selectedDim selected dim    
    def populateLengths(self, selectedDim = None):
        selected = None
        self.dimTableWidget.clear()
        self.dimTableWidget.setRowCount(self.rank)
        
        while self.rank > len(self.lengths):
            self.lengths.append(None)
        
        headers = ["Length"]
        self.dimTableWidget.setColumnCount(len(headers))
        self.dimTableWidget.setHorizontalHeaderLabels(headers)	
        self.dimTableWidget.setVerticalHeaderLabels( [str(l+1) for l in range(self.rank)] )	
        for row, ln in enumerate(self.lengths):
            if ln:
                item = QTableWidgetItem(str(ln))
            else:
                item = QTableWidgetItem("")
            item.setData(Qt.UserRole, QVariant(long(row)))
            if selectedDim is not None and selectedDim == row:
                selected = item
            self.dimTableWidget.setItem(row, 0, item)
        self.dimTableWidget.resizeColumnsToContents()
        self.dimTableWidget.horizontalHeader().setStretchLastSection(True);
        if selected is not None:
            selected.setSelected(True)
            self.dimTableWidget.setCurrentItem(selected)
            self.dimTableWidget.editItem(selected)
            



    ## accepts input text strings
    # \brief It copies the dimensions name and type from lineEdit widgets and accept the dialog
    def accept(self):
        self.doc = unicode(self.docTextEdit.toPlainText())
        while len(self.lengths) > self.rank:
            self.lengths.pop()
        QDialog.accept(self)

if __name__ == "__main__":
    import sys

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
    
