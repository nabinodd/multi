# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shutdown_win_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Poweroff_ui(object):
    def setupUi(self, Poweroff_ui):
        Poweroff_ui.setObjectName("Poweroff_ui")
        Poweroff_ui.resize(240, 159)
        self.widget = QtWidgets.QWidget(Poweroff_ui)
        self.widget.setGeometry(QtCore.QRect(9, 9, 222, 135))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pin_lbl = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pin_lbl.setFont(font)
        self.pin_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.pin_lbl.setObjectName("pin_lbl")
        self.verticalLayout.addWidget(self.pin_lbl)
        spacerItem1 = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.pin_input = QtWidgets.QLineEdit(self.widget)
        self.pin_input.setObjectName("pin_input")
        self.verticalLayout.addWidget(self.pin_input)
        self.poweroff_btn = QtWidgets.QPushButton(self.widget)
        self.poweroff_btn.setObjectName("poweroff_btn")
        self.verticalLayout.addWidget(self.poweroff_btn)
        spacerItem2 = QtWidgets.QSpacerItem(20, 3, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)
        self.cancel_btn = QtWidgets.QPushButton(self.widget)
        self.cancel_btn.setObjectName("cancel_btn")
        self.verticalLayout.addWidget(self.cancel_btn)

        self.retranslateUi(Poweroff_ui)
        QtCore.QMetaObject.connectSlotsByName(Poweroff_ui)

    def retranslateUi(self, Poweroff_ui):
        _translate = QtCore.QCoreApplication.translate
        Poweroff_ui.setWindowTitle(_translate("Poweroff_ui", "Form"))
        self.pin_lbl.setText(_translate("Poweroff_ui", "Enter PIN"))
        self.poweroff_btn.setText(_translate("Poweroff_ui", "OK"))
        self.cancel_btn.setText(_translate("Poweroff_ui", "Cancel"))
