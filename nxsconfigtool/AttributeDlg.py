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
# \file AttributeDlg.py
# Attribute dialog class

""" attribute dialog """
import os

from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QMessageBox)
from PyQt5 import uic

# from .ui.ui_attributedlg import Ui_AttributeDlg
from .Errors import CharacterError

import logging
import sys
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "attributedlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a tag attribute
class AttributeDlg(QDialog):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(AttributeDlg, self).__init__(parent)

        # attribute name
        self.name = u''
        # attribute value
        self.value = u''

        # user interface
        self.ui = _formclass()
        self.ui.setupUi(self)

        self.__updateUi()

        self.ui.nameLineEdit.textEdited.connect(self.__updateUi)
        # self.connect(self.ui.nameLineEdit,
        #              SIGNAL("textEdited(QString)"), self.__updateUi)

    # updates attribute user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        enable = bool(self.ui.nameLineEdit.text())
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    # accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets
    #        and accept the dialog
    def accept(self):
        name = unicode(self.ui.nameLineEdit.text())

        try:
            if 1 in [c in name for c in '!"#$%&\'()*+,/;<=>?@[\\]^`{|}~']:
                raise CharacterError(
                    "Name contains one of forbidden characters")
            if len(name) == 0:
                raise CharacterError("Empty Name")
            if name[0] == '-':
                raise CharacterError("The first character of Name is '-'")

        except CharacterError as e:
            QMessageBox.warning(self, "Character Error", unicode(e))
            return
        self.name = name
        self.value = unicode(self.ui.valueLineEdit.text())

        QDialog.accept(self)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # attribute form
    form = AttributeDlg()
    form.show()
    app.exec_()

    if form.result():
        if form.name:
            logger.info("Attribute: %s = \'%s\'" % (form.name, form.value))
