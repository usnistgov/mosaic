# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'trajview/trajviewui.ui'
#
# Created: Thu Aug  7 15:54:56 2014
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(637, 385)
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.mpl_hist = MplWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mpl_hist.sizePolicy().hasHeightForWidth())
        self.mpl_hist.setSizePolicy(sizePolicy)
        self.mpl_hist.setMinimumSize(QtCore.QSize(0, 200))
        self.mpl_hist.setObjectName(_fromUtf8("mpl_hist"))
        self.verticalLayout.addWidget(self.mpl_hist)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ionicCurrentLabel = QtGui.QLabel(Dialog)
        self.ionicCurrentLabel.setObjectName(_fromUtf8("ionicCurrentLabel"))
        self.horizontalLayout.addWidget(self.ionicCurrentLabel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.nextBtn = QtGui.QToolButton(Dialog)
        self.nextBtn.setMinimumSize(QtCore.QSize(50, 0))
        self.nextBtn.setObjectName(_fromUtf8("nextBtn"))
        self.horizontalLayout.addWidget(self.nextBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.ionicCurrentLabel.setText(_translate("Dialog", "Mean", None))
        self.nextBtn.setText(_translate("Dialog", "-->", None))

from mplwidget import MplWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

