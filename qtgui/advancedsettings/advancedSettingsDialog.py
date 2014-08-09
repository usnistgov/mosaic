# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'advancedsettings/advancedSettingsDialog.ui'
#
# Created: Sat Aug  9 17:51:54 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_advancedSettingsDialog(object):
    def setupUi(self, advancedSettingsDialog):
        advancedSettingsDialog.setObjectName(_fromUtf8("advancedSettingsDialog"))
        advancedSettingsDialog.resize(337, 480)
        advancedSettingsDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtGui.QVBoxLayout(advancedSettingsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.settingsTextEdit = QtGui.QTextEdit(advancedSettingsDialog)
        self.settingsTextEdit.setObjectName(_fromUtf8("settingsTextEdit"))
        self.verticalLayout.addWidget(self.settingsTextEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelPushButton = QtGui.QPushButton(advancedSettingsDialog)
        self.cancelPushButton.setObjectName(_fromUtf8("cancelPushButton"))
        self.horizontalLayout.addWidget(self.cancelPushButton)
        self.savePushButton = QtGui.QPushButton(advancedSettingsDialog)
        self.savePushButton.setObjectName(_fromUtf8("savePushButton"))
        self.horizontalLayout.addWidget(self.savePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(advancedSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(advancedSettingsDialog)

    def retranslateUi(self, advancedSettingsDialog):
        advancedSettingsDialog.setWindowTitle(_translate("advancedSettingsDialog", "Advanced Settings", None))
        self.cancelPushButton.setText(_translate("advancedSettingsDialog", "Cancel", None))
        self.savePushButton.setText(_translate("advancedSettingsDialog", "Save", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    advancedSettingsDialog = QtGui.QDialog()
    ui = Ui_advancedSettingsDialog()
    ui.setupUi(advancedSettingsDialog)
    advancedSettingsDialog.show()
    sys.exit(app.exec_())

